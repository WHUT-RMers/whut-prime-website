from __future__ import annotations

import json
import io
import base64
import hashlib
import mimetypes
import os
import secrets
import shutil
import subprocess
import tempfile
import time
import zipfile
import xml.etree.ElementTree as ElementTree
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models import Sum
from django.http import FileResponse, Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.text import get_valid_filename

from .forms import CarouselImageField, RichTextWidget
from .models import (NewsArticle, NewsCoverSlide, NewsImage, NewsRevision,
                     NewsView, RecruitmentApplication, RecruitmentAttachment, RecruitmentSettings,
                     XiumiBinding)


class NewsArticleAdminForm(forms.ModelForm):
    carousel_uploads = CarouselImageField(
        label='上传轮播图片', required=False,
        help_text='推荐 1920×1080；每张至少 1200×675、最大 8 MB。多图按添加顺序轮播。',
    )
    body = forms.CharField(label='文章正文', widget=RichTextWidget, help_text='编辑区支持标题、列表、引用、链接和正文插图，右侧会同步显示官网阅读效果。')
    published_at = forms.DateTimeField(
        label='对外显示时间', required=False, input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        help_text='已发布：填写现在或过去的时间；定时发布：填写未来时间；草稿/下线可留空。',
    )

    class Meta:
        model = NewsArticle
        fields = '__all__'
        help_texts = {
            'title': '前台显示的主标题，建议 12–28 个字。',
            'slug': '留空即可自动生成；发布后不要轻易修改，以免旧链接失效。',
            'summary': '显示在资讯卡片上的简介，建议 50–110 个字。',
            'category': '例如：赛报、备赛、日常、招新、合作。',
            'image_focus': '主体在照片哪里就选哪里，前台裁切时会优先保留该区域。',
            'is_pinned': '勾选后排在资讯列表最前。',
            'is_featured': '勾选后显示在官网首页“最新动态”。',
            'external_url': '若有公众号、B站等原文，填完整网址；没有则留空。',
            'status': '草稿不会公开；已发布立即公开；定时发布到指定时间自动公开；下线会从前台隐藏。',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('cover', None)
        self.fields.pop('cover_caption', None)
        self.fields.pop('image_focus', None)
        self.fields['body'].widget.attrs['data-upload-url'] = reverse('admin:portal_news_upload_inline_image')
        cover_images = []
        if self.instance and self.instance.pk:
            self.fields['body'].widget.attrs['data-article-id'] = str(self.instance.pk)
            if self.instance.cover:
                cover_images.append({
                    'id': 'cover',
                    'url': reverse('admin:portal_news_file', args=[self.instance.pk, 'cover', 0]),
                    'caption': self.instance.cover_caption,
                })
            for slide in self.instance.cover_slides.all():
                cover_images.append({
                    'id': f'slide-{slide.pk}',
                    'url': reverse('admin:portal_news_file', args=[self.instance.pk, 'slide', slide.pk]),
                    'caption': slide.caption,
                })
        self.fields['carousel_uploads'].widget.attrs['data-saved-covers'] = json.dumps(cover_images, ensure_ascii=False)
        self.fields['body'].widget.attrs['data-cover-images'] = json.dumps(cover_images, ensure_ascii=False)

    def clean(self):
        cleaned_data = super().clean()
        self.carousel_files = self.files.getlist('carousel_uploads')
        self.carousel_captions = [caption.strip()[:160] for caption in self.data.getlist('carousel_upload_captions')]
        if not self.instance.pk and not self.carousel_files:
            raise forms.ValidationError('请至少上传一张轮播图片作为封面。')
        return cleaned_data


class RecruitmentApplicationAdminForm(forms.ModelForm):
    intended_groups = forms.MultipleChoiceField(
        label='意向组别', choices=RecruitmentApplication.GROUPS,
        widget=forms.CheckboxSelectMultiple, help_text='报名者选择的方向；可多选。',
    )
    interview_at = forms.DateTimeField(
        label='面试安排', required=False, input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        help_text='可留空；填写后供运营内部安排使用，不会公开给报名者。',
    )

    class Meta:
        model = RecruitmentApplication
        fields = '__all__'
        help_texts = {'internal_note': '仅后台管理员可见，可记录面试评价、跟进人或下一步安排。'}


class ImagePreviewMixin:
    def image_preview(self, obj):
        if not obj or not obj.pk or not obj.image:
            return '保存并上传图片后，将在这里显示缩略预览。'
        return format_html('<img class="portal-thumb" src="{}" alt="图片预览">', self.preview_url(obj))
    image_preview.short_description = '图片预览'


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    form = NewsArticleAdminForm
    change_list_template = 'admin/portal/newsarticle/change_list.html'
    change_form_template = 'admin/portal/newsarticle/change_form.html'
    list_display = ('title', 'category', 'status', 'is_pinned', 'is_featured', 'published_at', 'view_count', 'views_7d', 'trash_state', 'recycle_button')
    list_filter = ('status', 'category', 'is_pinned', 'is_featured', 'is_trashed')
    search_fields = ('title', 'summary', 'body')
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'metrics')
    # Do not use SimpleUI's inline list editing: it creates a misleading
    # "保存" button even though content publishing happens in the edit page.
    list_editable = ()
    inlines = ()
    actions = None
    fieldsets = (
        ('① 文章内容', {'fields': ('title', 'slug', 'summary', 'category', 'carousel_uploads', 'body')}),
        ('② 展示设置', {'fields': ('is_pinned', 'is_featured', 'external_url')}),
        ('③ 发布控制', {'fields': ('status', 'published_at')}),
        ('④ 数据与记录', {'fields': ('metrics', 'view_count', 'created_at', 'updated_at')}),
    )

    class Media:
        css = {'all': ('portal/admin_polish.css', 'portal/carousel_manager.css')}
        js = ('portal/carousel_manager.js', 'portal/admin_bulk_actions.js')

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard), name='portal_news_dashboard'),
            path('<int:pk>/trash/', self.admin_site.admin_view(self.trash), name='portal_news_trash'),
            path('<int:pk>/restore/', self.admin_site.admin_view(self.restore), name='portal_news_restore'),
            path('<int:pk>/purge/', self.admin_site.admin_view(self.purge), name='portal_news_purge'),
            path('upload-inline-image/', self.admin_site.admin_view(self.upload_inline_image), name='portal_news_upload_inline_image'),
            path('bulk/trash/', self.admin_site.admin_view(self.bulk_trash), name='portal_news_bulk_trash'),
            path('bulk/restore/', self.admin_site.admin_view(self.bulk_restore), name='portal_news_bulk_restore'),
            path('bulk/purge/', self.admin_site.admin_view(self.bulk_purge), name='portal_news_bulk_purge'),
            path('<int:pk>/file/<str:kind>/<int:item_id>/', self.admin_site.admin_view(self.news_file), name='portal_news_file'),
            path('<int:pk>/xiumi/', self.admin_site.admin_view(self.xiumi_edit), name='portal_news_xiumi'),
        ]
        return custom + urls

    def xiumi_edit(self, request, pk):
        """Open the official Xiumi bind flow, or show the one-time setup page.

        The signing secret stays server-side.  Xiumi's bind endpoint receives
        only the app id and the signed, short-lived request parameters.
        """
        article = get_object_or_404(NewsArticle, pk=pk)
        if not self.has_change_permission(request, article):
            raise PermissionDenied

        app_id = getattr(settings, 'XIUMI_APP_ID', '')
        app_secret = getattr(settings, 'XIUMI_APP_SECRET', '')
        if not app_id or not app_secret:
            return TemplateResponse(request, 'admin/portal/newsarticle/xiumi_setup.html', {
                **self.admin_site.each_context(request),
                'title': '秀米编辑',
                'article': article,
                'xiumi_configured': False,
                'xiumi_console_url': 'https://xiumi.us/#/user/ownerpartnerbind',
            })

        partner_user_id = f'admin:{request.user.pk}'
        binding = XiumiBinding.objects.filter(partner_user_id=partner_user_id).first()
        if binding:
            query = urlencode({'open_id': binding.open_id, 'article_id': article.xiumi_article_id or ''})
            return redirect(f"{getattr(settings, 'XIUMI_BASE_URL', 'https://xiumi.us').rstrip('/')}/auth/partner/edit?{query}")
        timestamp = str(int(time.time()))
        nonce = secrets.token_urlsafe(12)
        signature_parts = [app_secret, timestamp, nonce, partner_user_id]
        signature_source = ''.join(sorted(signature_parts))
        signature = hashlib.md5(
            hashlib.md5(signature_source.encode('utf-8')).hexdigest().encode('utf-8')
        ).hexdigest()
        query = urlencode({
            'signature': signature,
            'timestamp': timestamp,
            'nonce': nonce,
            'partner_user_id': partner_user_id,
            'appid': app_id,
            'bind_name': getattr(settings, 'XIUMI_BIND_NAME', 'WHUT PRIME 官网'),
        })
        return redirect(f"{getattr(settings, 'XIUMI_BASE_URL', 'https://xiumi.us').rstrip('/')}/auth/partner/bind?{query}")

    def upload_inline_image(self, request):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        article_id = request.POST.get('article_id')
        article = get_object_or_404(NewsArticle, pk=article_id) if article_id else None
        image_file = request.FILES.get('image')
        if not image_file:
            return HttpResponseBadRequest('请选择一张图片。')
        image = NewsImage(article=article, image=image_file, caption=request.POST.get('caption', '').strip())
        try:
            image.full_clean()
        except ValidationError as error:
            return JsonResponse({'error': error.messages[0]}, status=400)
        image.save()
        url = reverse('portal:news-content-image', args=[image.token])
        return JsonResponse({'url': url, 'default': url, 'id': image.pk})

    def dashboard(self, request):
        articles = NewsArticle.objects.live()
        return TemplateResponse(request, 'admin/portal/news_dashboard.html', {
            **self.admin_site.each_context(request), 'title': '资讯运营看板',
            'total_views': articles.aggregate(total=Sum('view_count'))['total'] or 0,
            'views_7d': NewsView.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count(),
            'views_30d': NewsView.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count(),
            'top_articles': articles.order_by('-view_count')[:10], 'recent_articles': articles.order_by('-published_at')[:8],
        })

    def _post_only(self, request):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

    def trash(self, request, pk):
        if (response := self._post_only(request)): return response
        article = get_object_or_404(NewsArticle, pk=pk); article.is_trashed = True; article.save(update_fields=['is_trashed'])
        self.message_user(request, '已移入回收站，前台立即隐藏。', messages.SUCCESS)
        return redirect('admin:portal_newsarticle_changelist')

    def restore(self, request, pk):
        if (response := self._post_only(request)): return response
        article = get_object_or_404(NewsArticle, pk=pk); article.is_trashed = False; article.save(update_fields=['is_trashed'])
        self.message_user(request, '已从回收站恢复。', messages.SUCCESS)
        return redirect('admin:portal_newsarticle_change', pk)

    def purge(self, request, pk):
        if (response := self._post_only(request)): return response
        article = get_object_or_404(NewsArticle, pk=pk)
        if not article.is_trashed:
            self.message_user(request, '请先移入回收站，才能永久删除。', messages.ERROR)
            return redirect('admin:portal_newsarticle_change', pk)
        article.delete(); self.message_user(request, '该资讯已永久删除。', messages.SUCCESS)
        return redirect('admin:portal_newsarticle_changelist')

    def _selected_articles(self, request):
        return NewsArticle.objects.filter(pk__in=request.POST.getlist('ids'))

    def bulk_trash(self, request):
        if (response := self._post_only(request)): return response
        count = self._selected_articles(request).filter(is_trashed=False).update(is_trashed=True)
        self.message_user(request, f'已将 {count} 篇资讯移入回收站。', messages.SUCCESS)
        return redirect('admin:portal_newsarticle_changelist')

    def bulk_restore(self, request):
        if (response := self._post_only(request)): return response
        count = self._selected_articles(request).filter(is_trashed=True).update(is_trashed=False)
        self.message_user(request, f'已恢复 {count} 篇资讯。', messages.SUCCESS)
        return redirect('admin:portal_newsarticle_changelist')

    def bulk_purge(self, request):
        if (response := self._post_only(request)): return response
        selected = self._selected_articles(request).filter(is_trashed=True)
        count = selected.count(); selected.delete()
        self.message_user(request, f'已永久删除 {count} 篇回收站资讯。', messages.SUCCESS)
        return redirect('admin:portal_newsarticle_changelist')

    def news_file(self, request, pk, kind, item_id):
        article = get_object_or_404(NewsArticle, pk=pk)
        if kind == 'cover':
            file_field = article.cover
        elif kind == 'slide':
            file_field = get_object_or_404(NewsCoverSlide, pk=item_id, article=article).image
        elif kind == 'body':
            file_field = get_object_or_404(NewsImage, pk=item_id, article=article).image
        else:
            raise Http404
        return FileResponse(file_field.open('rb'), content_type='image/*')

    @admin.display(description='封面预览')
    def cover_preview(self, obj):
        if not obj or not obj.pk or not obj.cover: return '上传后显示封面缩略图。'
        return format_html('<img class="portal-cover-preview" src="{}" alt="封面预览">', reverse('admin:portal_news_file', args=[obj.pk, 'cover', 0]))

    @admin.display(description='回收站')
    def trash_state(self, obj):
        return '回收站中' if obj.is_trashed else '正常'

    @admin.display(description='操作')
    def recycle_button(self, obj):
        if obj.is_trashed:
            return format_html(
                '<button type="button" class="portal-row-action portal-row-restore" data-url="{}" data-confirm="恢复《{}》到正常资讯？">恢复</button>'
                '<button type="button" class="portal-row-action portal-row-purge" data-url="{}" data-confirm="永久删除《{}》？此操作无法恢复。">永久删除</button>',
                reverse('admin:portal_news_restore', args=[obj.pk]), obj.title,
                reverse('admin:portal_news_purge', args=[obj.pk]), obj.title,
            )
        return format_html(
            '<button type="button" class="portal-row-action portal-row-trash" data-url="{}" data-confirm="将《{}》移入回收站？前台会立即隐藏。">删除</button>',
            reverse('admin:portal_news_trash', args=[obj.pk]), obj.title,
        )

    @admin.display(description='浏览数据')
    def metrics(self, obj):
        if not obj.pk: return '保存后即可查看浏览数据。'
        return f'近 7 天：{obj.views_7d} ｜近 30 天：{obj.views_30d} ｜总浏览：{obj.view_count}'

    def save_model(self, request, obj, form, change):
        if change:
            NewsRevision.objects.create(article=obj, snapshot={'title': obj.title, 'summary': obj.summary, 'category': obj.category, 'body': obj.body, 'status': obj.status, 'published_at': obj.published_at.isoformat() if obj.published_at else None}, note='后台保存前快照')
        carousel_files = getattr(form, 'carousel_files', [])
        carousel_captions = getattr(form, 'carousel_captions', [])
        if not change:
            obj.cover = carousel_files[0]
            obj.cover_caption = carousel_captions[0] if carousel_captions else ''
        elif 'carousel_saved_caption_cover' in request.POST:
            obj.cover_caption = request.POST.get('carousel_saved_caption_cover', '').strip()[:160]
        super().save_model(request, obj, form, change)
        # 新建资讯时，编辑器允许先上传正文图；保存后按正文中的稳定图片地址完成归属。
        import re
        tokens = re.findall(r'/api/news/content-images/([0-9a-fA-F-]{36})/', obj.body or '')
        if tokens:
            NewsImage.objects.filter(token__in=tokens, article__isnull=True).update(article=obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        article = form.instance
        files = getattr(form, 'carousel_files', [])
        captions = getattr(form, 'carousel_captions', [])
        for slide in article.cover_slides.all():
            caption_key = f'carousel_saved_caption_slide_{slide.pk}'
            if caption_key in request.POST:
                slide.caption = request.POST.get(caption_key, '').strip()[:160]
                slide.save(update_fields=['caption'])
        if not files:
            return
        if not change:
            files = files[1:]
            captions = captions[1:]
        start = (NewsCoverSlide.objects.filter(article=article).order_by('-sort_order').values_list('sort_order', flat=True).first() or 0) + 1
        for index, image_file in enumerate(files, start=start):
            caption_index = index - start
            caption = captions[caption_index] if caption_index < len(captions) else ''
            NewsCoverSlide.objects.create(article=article, image=image_file, caption=caption, sort_order=index)

    @admin.display(description='当前轮播预览')
    def cover_gallery(self, obj):
        if not obj or not obj.pk or not obj.cover:
            return format_html(
                '<div class="portal-carousel-empty">{}</div>',
                '选择图片并保存后，这里会显示统一比例的轮播预览。',
            )
        cards = [
            format_html(
                '<figure class="portal-carousel-card"><img src="{}" alt="轮播第 1 张"><figcaption><b>01</b> 图片 01</figcaption></figure>',
                reverse('admin:portal_news_file', args=[obj.pk, 'cover', 0]),
            )
        ]
        for index, slide in enumerate(obj.cover_slides.all(), start=2):
            cards.append(format_html(
                '<figure class="portal-carousel-card"><img src="{}" alt="轮播第 {} 张"><figcaption><b>{:02d}</b> 图片 {:02d}</figcaption></figure>',
                reverse('admin:portal_news_file', args=[obj.pk, 'slide', slide.pk]), index, index, index,
            ))
        return format_html(
            '<div class="portal-carousel-gallery">{}</div>',
            format_html_join('', '{}', ((card,) for card in cards)),
        )


@admin.register(RecruitmentApplication)
class RecruitmentApplicationAdmin(admin.ModelAdmin):
    form = RecruitmentApplicationAdminForm
    change_list_template = 'admin/portal/recruitmentapplication/change_list.html'
    list_display = ('application_no', 'name', 'preview_link', 'college', 'major_class', 'primary_group_display', 'adjustment_display', 'status', 'created_at', 'resume_link')
    list_filter = ('primary_choice', 'status', 'accepts_adjustment', 'created_at')
    search_fields = ('application_no', 'name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class')
    readonly_fields = ('application_no', 'created_at', 'updated_at', 'photo_preview', 'resume_link', 'attachments_display')
    list_editable = ('status',)
    fields = ('application_no', 'name', 'gender', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class', 'photo', 'photo_preview', 'primary_choice', 'accepts_adjustment', 'second_choice', 'introduction', 'honors', 'roles', 'technical_foundation', 'experience', 'resume_link', 'attachments_display', 'status', 'interview_at', 'internal_note', 'created_at', 'updated_at')

    class Media:
        css = {'all': ('portal/admin_polish.css', 'portal/recruitment_preview.css')}
        js = ('portal/recruitment_pdf_viewer.js', 'portal/recruitment_material_preview_v3.js')

    def get_urls(self):
        return [
            path('export-filtered/', self.admin_site.admin_view(self.export_filtered), name='portal_recruitment_export_filtered'),
            path('export-all/', self.admin_site.admin_view(self.export_all), name='portal_recruitment_export_all'),
            path('<int:pk>/preview/', self.admin_site.admin_view(self.application_preview), name='portal_recruitmentapplication_preview'),
            path('<int:pk>/photo-preview/', self.admin_site.admin_view(self.photo_preview_file), name='portal_recruitment_photo_preview'),
            path('<int:pk>/resume-preview/', self.admin_site.admin_view(self.resume_preview), name='portal_recruitment_resume_preview'),
            path('<int:pk>/attachment/<int:attachment_id>/', self.admin_site.admin_view(self.attachment_file), name='portal_recruitment_attachment_file'),
            path('<int:pk>/attachment/<int:attachment_id>/preview-data/', self.admin_site.admin_view(self.attachment_preview_data), name='portal_recruitment_attachment_preview_data'),
            path('<int:pk>/attachment/<int:attachment_id>/preview-entry/', self.admin_site.admin_view(self.attachment_preview_entry), name='portal_recruitment_attachment_preview_entry'),
            path('<int:pk>/attachment/<int:attachment_id>/rendered-preview/', self.admin_site.admin_view(self.attachment_rendered_preview), name='portal_recruitment_attachment_rendered_preview'),
        ] + super().get_urls()

    def get_queryset(self, request):
        applications = super().get_queryset(request).prefetch_related('attachments')
        primary = request.GET.get('primary_choice')
        status = request.GET.get('status')
        adjustment = request.GET.get('accepts_adjustment')
        if primary:
            applications = applications.filter(primary_choice=primary)
        if status:
            applications = applications.filter(status=status)
        if adjustment in {'0', '1'}:
            applications = applications.filter(accepts_adjustment=adjustment == '1')
        return applications

    def _filtered_applications(self, request):
        change_list = self.get_changelist_instance(request)
        return change_list.get_queryset(request).prefetch_related('attachments')

    def _export_archive(self, applications, filename, grouped=False):
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill

        groups = dict(RecruitmentApplication.GROUPS)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = '报名汇总'
            headers = ['报名编号', '姓名', '性别', '第一志愿', '服从调剂', '第二志愿/统筹', '审核状态', '学院', '专业与班级', 'QQ', '微信', '邮箱', '手机', '个人简介', '个人荣誉', '任职情况', '技术基础', '项目/竞赛经历', '照片', '报名时间', '附件数量']
            items = list(applications)
            buckets = {key: [] for key in groups}
            if grouped:
                for application in items:
                    buckets.setdefault(application.primary_choice, []).append(application)
            else:
                buckets = {'筛选结果': items}
            row = 1
            for key, group_items in buckets.items():
                if grouped:
                    sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(headers))
                    title = sheet.cell(row=row, column=1, value=f'{groups.get(key, key)} · 第一志愿报名（{len(group_items)} 人）')
                    title.font = Font(bold=True, color='FFFFFF', size=12)
                    title.fill = PatternFill('solid', fgColor='176B91')
                    row += 1
                sheet.append(headers)
                for cell in sheet[row]:
                    cell.font = Font(bold=True, color='FFFFFF')
                    cell.fill = PatternFill('solid', fgColor='159A70')
                row += 1
                for application in group_items:
                    second = groups.get(application.second_choice, '接受统筹安排') if application.accepts_adjustment else '不服从调剂'
                    sheet.append([application.application_no, application.name, application.get_gender_display() or '—', groups.get(application.primary_choice, application.primary_choice), '是' if application.accepts_adjustment else '否', second, application.get_status_display(), application.college, application.major_class, application.qq, application.wechat, application.email, application.phone, application.introduction, application.honors, application.roles, application.technical_foundation, application.experience, '已上传' if application.photo else '未上传', application.created_at.replace(tzinfo=None), application.attachments.count()])
                    row += 1
                    folder_group = groups.get(application.primary_choice, application.primary_choice) if grouped else '报名材料'
                    folder = f'{folder_group}/{get_valid_filename(application.application_no)}_{get_valid_filename(application.name)}'
                    for attachment in application.attachments.all():
                        if attachment.file:
                            archive.writestr(f'{folder}/{get_valid_filename(attachment.original_name)}', attachment.file.read())
                    if application.photo:
                        extension = application.photo.name.rsplit('.', 1)[-1].lower() if '.' in application.photo.name else 'jpg'
                        archive.writestr(f'{folder}/个人照片.{get_valid_filename(extension)}', application.photo.read())
                row += 1 if grouped else 0
            sheet.freeze_panes = 'A2'
            for column, width in {'A':18,'B':12,'C':10,'D':12,'E':12,'F':18,'G':12,'H':18,'I':28,'J':14,'K':18,'L':28,'M':16,'N':16,'O':34,'P':30,'Q':30,'R':34,'S':38,'T':12,'U':20,'V':12}.items():
                sheet.column_dimensions[column].width = width
            xlsx = io.BytesIO(); workbook.save(xlsx)
            archive.writestr('报名信息.xlsx', xlsx.getvalue())
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=filename)

    def export_filtered(self, request):
        return self._export_archive(self._filtered_applications(request), 'PRIME-筛选报名导出.zip')

    def export_all(self, request):
        return self._export_archive(RecruitmentApplication.objects.prefetch_related('attachments').all(), 'PRIME-全部报名归档.zip', grouped=True)

    def _preview_query(self, request):
        query = request.GET.copy()
        query.pop('p', None)
        return query.urlencode()

    @admin.display(description='报名表')
    def preview_link(self, obj):
        return format_html(
            '<a class="recruitment-application-preview-link" href="{}">查看报名表</a>',
            reverse('admin:portal_recruitmentapplication_preview', args=[obj.pk]),
        )

    @admin.display(description='照片预览')
    def photo_preview(self, obj):
        if not obj or not obj.pk or not obj.photo:
            return '未上传照片'
        return format_html(
            '<img class="recruitment-photo-admin-preview" src="{}" alt="{}">',
            reverse('admin:portal_recruitment_photo_preview', args=[obj.pk]), obj.name or '报名者照片',
        )

    def application_preview(self, request, pk):
        application = get_object_or_404(self.get_queryset(request), pk=pk)
        applications = list(self._filtered_applications(request))
        try:
            position = next(index for index, item in enumerate(applications) if item.pk == application.pk)
        except StopIteration:
            applications = [application]
            position = 0
        query = self._preview_query(request)

        def navigation_url(item):
            url = reverse('admin:portal_recruitmentapplication_preview', args=[item.pk])
            return f'{url}?{query}' if query else url

        groups = dict(RecruitmentApplication.GROUPS)
        return TemplateResponse(request, 'admin/portal/recruitmentapplication/preview.html', {
            **self.admin_site.each_context(request),
            'title': f'{application.name} · 报名表预览',
            'opts': self.model._meta,
            'application': application,
            'groups': groups,
            'position': position + 1,
            'total': len(applications),
            'previous_url': navigation_url(applications[position - 1]) if position > 0 else '',
            'next_url': navigation_url(applications[position + 1]) if position + 1 < len(applications) else '',
            'list_url': reverse('admin:portal_recruitmentapplication_changelist') + (f'?{query}' if query else ''),
            'edit_url': reverse('admin:portal_recruitmentapplication_change', args=[application.pk]),
            'photo_url': reverse('admin:portal_recruitment_photo_preview', args=[application.pk]) if application.photo else '',
            'resume_url': reverse('admin:portal_recruitment_resume_preview', args=[application.pk]) if application.resume else '',
            'attachments': application.attachments.all(),
            'materials_json': json.dumps(self._preview_materials(application), ensure_ascii=False),
        })

    def photo_preview_file(self, request, pk):
        application = get_object_or_404(RecruitmentApplication, pk=pk)
        if not application.photo:
            raise Http404('该报名者没有上传照片。')
        content_type = mimetypes.guess_type(application.photo.name)[0] or 'image/jpeg'
        return FileResponse(application.photo.open('rb'), content_type=content_type)

    def resume_preview(self, request, pk):
        application = get_object_or_404(RecruitmentApplication, pk=pk)
        if not application.resume:
            raise Http404('该报名者没有上传简历。')
        return FileResponse(application.resume.open('rb'), content_type='application/pdf')

    def attachment_file(self, request, pk, attachment_id):
        attachment = get_object_or_404(RecruitmentAttachment, pk=attachment_id, application_id=pk)
        content_type = mimetypes.guess_type(attachment.original_name)[0] or 'application/octet-stream'
        download = request.GET.get('download') == '1'
        return FileResponse(
            attachment.file.open('rb'), content_type=content_type,
            as_attachment=download, filename=attachment.original_name if download else None,
        )

    PREVIEW_ENTRY_LIMIT = 30 * 1024 * 1024
    DOCX_IMAGE_LIMIT = 6 * 1024 * 1024
    OFFICE_RENDER_LIMIT = 80 * 1024 * 1024
    OFFICE_RENDER_SUFFIXES = {
        'doc', 'docx', 'docm', 'wps', 'rtf', 'odt',
        'xls', 'xlsx', 'xlsm', 'et', 'ods',
        'ppt', 'pptx', 'pptm', 'dps', 'odp',
    }
    # These are the WPS desktop formats verified on this Windows host. PPT is
    # intentionally left for the Microsoft Office fallback below because the
    # installed PowerPoint COM server is the reliable renderer for slides.
    WPS_RENDER_SUFFIXES = {
        'doc', 'docx', 'docm', 'wps', 'rtf', 'odt',
        'xls', 'xlsx', 'xlsm', 'et', 'ods',
    }

    @staticmethod
    def _suffix(name):
        return name.rsplit('.', 1)[-1].lower() if '.' in name else ''

    @staticmethod
    def _preview_kind(name):
        suffix = RecruitmentApplicationAdmin._suffix(name)
        if suffix == 'pdf':
            return 'pdf'
        if suffix in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'avif', 'svg'}:
            return 'image'
        if suffix in {'mp4', 'mov', 'webm', 'm4v', 'ogv', 'avi', 'mkv'}:
            return 'video'
        if suffix in {'mp3', 'wav', 'm4a', 'ogg', 'oga', 'flac', 'aac'}:
            return 'audio'
        if suffix in {'txt', 'md', 'csv', 'json', 'log', 'xml', 'html', 'htm', 'css', 'js', 'ts', 'tsx', 'jsx', 'vue', 'yaml', 'yml', 'ini', 'toml', 'sql', 'py', 'java', 'c', 'cpp', 'h', 'sh', 'bat'}:
            return 'text'
        if suffix in RecruitmentApplicationAdmin.OFFICE_RENDER_SUFFIXES | {'zip'}:
            return 'structured'
        return 'other'

    @classmethod
    def _wps_executable(cls):
        """Return a locally installed WPS Writer executable when available."""
        configured = os.environ.get('PRIME_WPS_EXECUTABLE', '').strip()
        candidates = [Path(configured)] if configured else []
        for root_name in ('LOCALAPPDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)'):
            root = os.environ.get(root_name, '').strip()
            if root:
                candidates.extend(Path(root).glob('Kingsoft/WPS Office/*/office6/wps.exe'))
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    @classmethod
    def _libreoffice_executable(cls):
        configured = os.environ.get('PRIME_LIBREOFFICE_EXECUTABLE', '').strip()
        candidates = [Path(configured)] if configured else []
        for command in ('soffice', 'libreoffice'):
            located = shutil.which(command)
            if located:
                candidates.append(Path(located))
        for root_name in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
            root = os.environ.get(root_name, '').strip()
            if root:
                candidates.extend([
                    Path(root) / 'LibreOffice' / 'program' / 'soffice.exe',
                    Path(root) / 'libreoffice' / 'program' / 'soffice.exe',
                ])
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    @classmethod
    def _microsoft_office_executable(cls, suffix):
        if os.name != 'nt':
            return None
        folder = (
            'WINWORD.EXE' if suffix in {'doc', 'docx', 'docm', 'wps', 'rtf', 'odt'} else
            'EXCEL.EXE' if suffix in {'xls', 'xlsx', 'xlsm', 'et', 'ods'} else
            'POWERPNT.EXE'
        )
        candidates = []
        for root_name in ('PROGRAMFILES', 'PROGRAMFILES(X86)'):
            root = os.environ.get(root_name, '').strip()
            if root:
                base = Path(root) / 'Microsoft Office'
                candidates.extend(base.glob(f'root/Office*/{folder}'))
                candidates.extend(base.glob(f'Office*/{folder}'))
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    @classmethod
    @lru_cache(maxsize=None)
    def _renderer_for_suffix(cls, suffix):
        """Pick a renderer on the server; the end user's Office software is irrelevant."""
        if suffix not in cls.OFFICE_RENDER_SUFFIXES:
            return ''
        preference = os.environ.get('PRIME_DOCUMENT_RENDERER', 'auto').strip().lower()
        if preference in {'wps', 'auto'} and suffix in cls.WPS_RENDER_SUFFIXES and cls._wps_executable():
            return 'wps'
        if preference in {'libreoffice', 'auto'} and cls._libreoffice_executable():
            return 'libreoffice'
        if preference in {'microsoft', 'office', 'auto'} and cls._microsoft_office_executable(suffix):
            return 'microsoft'
        return ''

    @classmethod
    def _office_render_cache(cls, content, filename):
        if len(content) > cls.OFFICE_RENDER_LIMIT:
            raise ValueError('office file is too large for online rendering')
        suffix = cls._suffix(filename) or 'bin'
        digest = hashlib.sha256(content).hexdigest()
        cache_dir = Path(tempfile.gettempdir()) / 'whut-prime-office-previews'
        cache_dir.mkdir(parents=True, exist_ok=True)
        source = cache_dir / f'{digest}.{suffix}'
        target = cache_dir / f'{digest}.pdf'
        if target.is_file() and target.stat().st_size:
            return target
        source.write_bytes(content)
        return source, target

    @classmethod
    def _render_office_to_pdf(cls, content, filename):
        """Convert an Office file to PDF with a locally installed office engine."""
        cached = cls._office_render_cache(content, filename)
        if isinstance(cached, Path):
            return cached
        source, target = cached
        suffix = cls._suffix(filename)
        renderer = cls._renderer_for_suffix(suffix)
        if not renderer:
            raise RuntimeError('no Office renderer is installed')

        if renderer == 'libreoffice':
            command = [
                str(cls._libreoffice_executable()), '--headless', '--convert-to', 'pdf',
                '--outdir', str(target.parent), str(source),
            ]
            subprocess.run(command, check=True, capture_output=True, timeout=120)
            if not target.is_file():
                raise RuntimeError('LibreOffice did not produce a PDF preview')
            return target

        if renderer == 'microsoft':
            return cls._render_office_with_microsoft(source, target, suffix)

        return cls._render_office_with_wps(source, target, suffix)

    @classmethod
    def _render_office_with_wps(cls, source, target, suffix):
        """Export through WPS desktop automation without showing its window."""

        import pythoncom
        import win32com.client

        writer_suffixes = {'doc', 'docx', 'docm', 'wps', 'rtf', 'odt'}
        sheet_suffixes = {'xls', 'xlsx', 'xlsm', 'et', 'ods'}
        presentation_suffixes = {'ppt', 'pptx', 'pptm', 'dps', 'odp'}
        progids = (
            ('Kwps.Application', 'WPS.Application', 'KWPS.Application') if suffix in writer_suffixes else
            ('Ket.Application', 'ET.Application') if suffix in sheet_suffixes else
            ('Kwpp.Application', 'WPP.Application') if suffix in presentation_suffixes else
            ()
        )
        if not progids:
            raise ValueError(f'unsupported office suffix: {suffix}')

        pythoncom.CoInitialize()
        app = None
        document = None
        workbook = None
        presentation = None
        try:
            if suffix not in writer_suffixes and suffix not in sheet_suffixes:
                # PowerPoint's ExportAsFixedFormat COM method requires its
                # complete optional argument list and is more reliable via
                # the normal Dispatch entry point.
                app = win32com.client.Dispatch('PowerPoint.Application')
            else:
                for progid in progids:
                    try:
                        app = win32com.client.DispatchEx(progid)
                        break
                    except Exception:
                        app = None
            if app is None:
                raise RuntimeError('WPS COM automation is unavailable')
            try:
                app.Visible = False
                app.DisplayAlerts = False
            except Exception:
                pass

            if suffix in writer_suffixes:
                document = app.Documents.Open(str(source), ReadOnly=True, AddToRecentFiles=False, Visible=False)
                try:
                    document.ExportAsFixedFormat(str(target), 17)
                except Exception:
                    document.SaveAs(str(target), 17)
            elif suffix in sheet_suffixes:
                workbook = app.Workbooks.Open(str(source), ReadOnly=True)
                workbook.ExportAsFixedFormat(0, str(target))
            else:
                presentation = app.Presentations.Open(str(source), ReadOnly=True, Untitled=True, WithWindow=False)
                presentation.ExportAsFixedFormat(str(target), 2)
        finally:
            for item in (document, workbook, presentation):
                if item is not None:
                    try:
                        item.Close(False)
                    except Exception:
                        pass
            if app is not None:
                try:
                    app.Quit()
                except Exception:
                    pass
            pythoncom.CoUninitialize()

        if not target.is_file() or not target.stat().st_size:
            raise RuntimeError('WPS did not produce a PDF preview')
        return target

    @classmethod
    def _render_office_with_microsoft(cls, source, target, suffix):
        """Export through Microsoft Office COM when it is the available engine."""
        import pythoncom
        import win32com.client

        writer_suffixes = {'doc', 'docx', 'docm', 'wps', 'rtf', 'odt'}
        sheet_suffixes = {'xls', 'xlsx', 'xlsm', 'et', 'ods'}
        progids = (
            ('Word.Application',) if suffix in writer_suffixes else
            ('Excel.Application',) if suffix in sheet_suffixes else
            ('PowerPoint.Application',)
        )
        pythoncom.CoInitialize()
        app = None
        document = None
        workbook = None
        presentation = None
        try:
            for progid in progids:
                try:
                    app = win32com.client.DispatchEx(progid)
                    break
                except Exception:
                    app = None
            if app is None:
                raise RuntimeError('Microsoft Office COM automation is unavailable')
            try:
                app.Visible = False
                app.DisplayAlerts = 0
            except Exception:
                pass
            if suffix in writer_suffixes:
                document = app.Documents.Open(str(source), ReadOnly=True, AddToRecentFiles=False, Visible=False)
                document.ExportAsFixedFormat(str(target), 17)
            elif suffix in sheet_suffixes:
                workbook = app.Workbooks.Open(str(source), ReadOnly=True)
                workbook.ExportAsFixedFormat(0, str(target))
            else:
                # PowerPoint refuses a hidden Application.Visible=False COM
                # session for file conversion. Keep the window minimized so
                # the server can still render PPT/PPTX without interrupting
                # the operator's desktop, then save as a PDF.
                app.Visible = True
                try:
                    app.WindowState = 2  # ppWindowMinimized
                except Exception:
                    pass
                presentation = app.Presentations.Open(str(source), False, False, False)
                presentation.SaveAs(str(target), 32)  # ppSaveAsPDF
        finally:
            for item in (document, workbook, presentation):
                if item is not None:
                    try:
                        item.Close(False)
                    except Exception:
                        pass
            if app is not None:
                try:
                    app.Quit()
                except Exception:
                    pass
            pythoncom.CoUninitialize()
        if not target.is_file() or not target.stat().st_size:
            raise RuntimeError('Microsoft Office did not produce a PDF preview')
        return target

    @classmethod
    def _structured_preview(cls, title, suffix, content):
        if suffix == 'docx':
            from docx import Document
            document = Document(io.BytesIO(content))
            paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
            tables = []
            for table in document.tables[:20]:
                rows = []
                for row in table.rows[:80]:
                    rows.append([cell.text.strip()[:240] for cell in row.cells[:20]])
                tables.append({'rows': rows})
            images = []
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as archive:
                    if not paragraphs and not tables:
                        paragraphs = cls._docx_xml_paragraphs(archive)
                    used = 0
                    for name in archive.namelist():
                        if not name.startswith('word/media/') or name.endswith('/'):
                            continue
                        image = archive.read(name)
                        if not image or len(image) > cls.DOCX_IMAGE_LIMIT or used + len(image) > cls.DOCX_IMAGE_LIMIT:
                            continue
                        mime = mimetypes.guess_type(name)[0] or 'application/octet-stream'
                        images.append({
                            'name': name.rsplit('/', 1)[-1],
                            'src': f'data:{mime};base64,{base64.b64encode(image).decode("ascii")}',
                        })
                        used += len(image)
                        if len(images) >= 8:
                            break
            except zipfile.BadZipFile:
                pass
            return {
                'kind': 'document', 'title': title,
                'paragraphs': paragraphs[:240], 'tables': tables, 'images': images,
            }
        if suffix in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'avif', 'svg'}:
            return {'kind': 'image', 'title': title}
        if suffix == 'xlsx':
            from openpyxl import load_workbook
            workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            sheets = []
            for worksheet in list(workbook.worksheets)[:12]:
                rows = []
                for values in worksheet.iter_rows(max_row=160, max_col=30, values_only=True):
                    rows.append(['' if value is None else str(value)[:240] for value in values])
                sheets.append({'name': worksheet.title, 'rows': rows})
            return {'kind': 'spreadsheet', 'title': title, 'sheets': sheets}
        if suffix == 'pptx':
            from pptx import Presentation
            presentation = Presentation(io.BytesIO(content))
            slides = []
            for number, slide in enumerate(presentation.slides, start=1):
                texts = [shape.text.strip() for shape in slide.shapes if getattr(shape, 'has_text_frame', False) and shape.text.strip()]
                slides.append({'number': number, 'text': texts[:40]})
            return {'kind': 'presentation', 'title': title, 'slides': slides}
        return None

    @staticmethod
    def _docx_xml_paragraphs(archive):
        """Read text boxes and drawing-layer text that python-docx omits."""
        word_namespace = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        paragraph_tag = f'{{{word_namespace}}}p'
        text_tag = f'{{{word_namespace}}}t'
        paragraphs = []
        seen = set()
        parts = [
            name for name in archive.namelist()
            if name.startswith('word/') and name.endswith('.xml')
            and name.rsplit('/', 1)[-1] in {'document.xml', 'footnotes.xml', 'endnotes.xml'}
        ]
        for part in parts:
            try:
                root = ElementTree.fromstring(archive.read(part))
            except (ElementTree.ParseError, KeyError):
                continue
            for paragraph in root.iter(paragraph_tag):
                if any(node is not paragraph and node.tag == paragraph_tag for node in paragraph.iter()):
                    continue
                text = ''.join(node.text or '' for node in paragraph.iter(text_tag)).strip()
                if text and text not in seen:
                    seen.add(text)
                    paragraphs.append(text[:2000])
        return paragraphs

    @classmethod
    def _zip_entries(cls, content, entry_url, data_url, rendered_url=''):
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            files = []
            for info in archive.infolist():
                if info.is_dir():
                    continue
                query = urlencode({'entry': info.filename})
                item = {
                    'path': info.filename,
                    'name': info.filename.rsplit('/', 1)[-1],
                    'size': info.file_size,
                    'kind': cls._preview_kind(info.filename),
                    'preview': f'{entry_url}?{query}',
                    'dataPreview': f'{data_url}?{query}',
                    'download': f'{entry_url}?{query}&download=1',
                }
                if rendered_url and cls._renderer_for_suffix(cls._suffix(info.filename)):
                    item['renderedPreview'] = f'{rendered_url}?{query}'
                files.append(item)
        return files

    def _attachment_content(self, attachment, entry=''):
        with attachment.file.open('rb') as uploaded:
            content = uploaded.read()
        if not entry:
            return content, attachment.original_name
        if self._suffix(attachment.original_name) != 'zip':
            raise Http404('只有 ZIP 文件支持内部条目预览。')
        normalized = entry.replace('\\', '/')
        parts = [part for part in normalized.split('/') if part not in {'', '.'}]
        if any(part == '..' for part in parts) or not parts:
            raise Http404('压缩包条目路径无效。')
        entry_name = '/'.join(parts)
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                info = archive.getinfo(entry_name)
                if info.is_dir() or info.file_size > self.PREVIEW_ENTRY_LIMIT:
                    raise Http404('该条目过大，无法在线预览。')
                return archive.read(info), info.filename
        except KeyError as error:
            raise Http404('压缩包中不存在该文件。') from error
        except zipfile.BadZipFile as error:
            raise Http404('ZIP 文件损坏。') from error

    def attachment_preview_entry(self, request, pk, attachment_id):
        attachment = get_object_or_404(RecruitmentAttachment, pk=attachment_id, application_id=pk)
        content, name = self._attachment_content(attachment, request.GET.get('entry', ''))
        content_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'
        response = HttpResponse(content, content_type=content_type)
        safe_name = get_valid_filename(name.rsplit('/', 1)[-1])
        disposition = 'attachment' if request.GET.get('download') == '1' else 'inline'
        response['Content-Disposition'] = f'{disposition}; filename="{safe_name}"'
        return response

    def attachment_rendered_preview(self, request, pk, attachment_id):
        """Return a WPS-exported PDF for an Office file or a ZIP child file."""
        attachment = get_object_or_404(RecruitmentAttachment, pk=attachment_id, application_id=pk)
        content, title = self._attachment_content(attachment, request.GET.get('entry', ''))
        if self._suffix(title) not in self.OFFICE_RENDER_SUFFIXES or not self._renderer_for_suffix(self._suffix(title)):
            raise Http404('该文件不是可转换的 Office 文档。')
        try:
            rendered = self._render_office_to_pdf(content, title)
        except (ImportError, OSError, RuntimeError, ValueError):
            return HttpResponse('当前服务器没有可用的 Office 文档渲染器。', status=503, content_type='text/plain; charset=utf-8')
        response = FileResponse(rendered.open('rb'), content_type='application/pdf')
        safe_name = get_valid_filename(title.rsplit('/', 1)[-1].rsplit('.', 1)[0]) or 'document'
        response['Content-Disposition'] = f'inline; filename="{safe_name}.pdf"'
        return response

    def attachment_preview_data(self, request, pk, attachment_id):
        """Extract an inspectable preview for common documents and ZIP entries."""
        attachment = get_object_or_404(RecruitmentAttachment, pk=attachment_id, application_id=pk)
        entry = request.GET.get('entry', '')
        try:
            content, title = self._attachment_content(attachment, entry)
            suffix = self._suffix(title)
            structured = self._structured_preview(title, suffix, content)
            if structured:
                return JsonResponse(structured)
            if suffix == 'zip':
                entry_url = reverse('admin:portal_recruitment_attachment_preview_entry', args=[pk, attachment.pk])
                data_url = reverse('admin:portal_recruitment_attachment_preview_data', args=[pk, attachment.pk])
                rendered_url = reverse('admin:portal_recruitment_attachment_rendered_preview', args=[pk, attachment.pk])
                files = self._zip_entries(content, entry_url, data_url, rendered_url)
                return JsonResponse({'kind': 'archive', 'title': title, 'files': files, 'total': len(files)})
        except (ValueError, OSError, zipfile.BadZipFile, ImportError):
            pass
        return JsonResponse({'kind': 'unsupported', 'title': title if 'title' in locals() else attachment.original_name, 'message': '此文件无法生成在线预览，请下载后使用对应软件打开。'})

    @admin.display(description='意向组别')
    def groups_display(self, obj):
        mapping = dict(RecruitmentApplication.GROUPS)
        return '、'.join(mapping.get(key, key) for key in obj.intended_groups)

    @admin.display(description='第一志愿', ordering='primary_choice')
    def primary_group_display(self, obj):
        return dict(RecruitmentApplication.GROUPS).get(obj.primary_choice, obj.primary_choice)

    @admin.display(description='服从调剂')
    def adjustment_display(self, obj):
        if not obj.accepts_adjustment:
            return '否'
        return dict(RecruitmentApplication.GROUPS).get(obj.second_choice, '接受统筹安排')

    @admin.display(description='简历')
    def resume_link(self, obj):
        if not obj.pk:
            return '保存后可下载'
        materials = self._preview_materials(obj)
        if not materials:
            return '未上传附件'
        return format_html(
            '<span class="recruitment-material-actions">'
            '<a class="recruitment-download-link" href="{}">下载全部附件</a>'
            '<button type="button" class="recruitment-preview-trigger" data-materials="{}" '
            'title="预览附件" aria-label="预览附件">&#128065;</button></span>',
            reverse('portal:resume-download', args=[obj.pk]), json.dumps(materials, ensure_ascii=False),
        )

    @admin.display(description='附加材料')
    def attachments_display(self, obj):
        if not obj.pk:
            return '保存后显示附件。'
        materials = self._preview_materials(obj)
        if not materials:
            return '无附加材料'
        return format_html_join(
            '<br>',
            '<span class="recruitment-attachment-item">{} '
            '<a href="{}">下载</a> '
            '<button type="button" class="recruitment-preview-trigger" data-materials="{}" title="预览 {}" aria-label="预览 {}">&#128065;</button></span>',
            ((item['name'], item['download'], json.dumps([item], ensure_ascii=False), item['name'], item['name']) for item in materials),
        )

    def _preview_materials(self, obj):
        materials = []
        for attachment in obj.attachments.all():
            if attachment.file:
                preview_url = reverse('admin:portal_recruitment_attachment_file', args=[obj.pk, attachment.pk])
                materials.append({
                    'name': attachment.original_name,
                    'preview': preview_url,
                    'download': f'{preview_url}?download=1',
                    'dataPreview': reverse('admin:portal_recruitment_attachment_preview_data', args=[obj.pk, attachment.pk]),
                    **({
                        'renderedPreview': reverse('admin:portal_recruitment_attachment_rendered_preview', args=[obj.pk, attachment.pk]),
                    } if self._renderer_for_suffix(self._suffix(attachment.original_name)) else {}),
                })
        if obj.resume and not any(item['name'] == '简历.pdf' for item in materials):
            preview_url = reverse('admin:portal_recruitment_resume_preview', args=[obj.pk])
            materials.append({
                'name': '简历.pdf',
                'preview': preview_url,
                'download': reverse('portal:resume-download', args=[obj.pk]),
            })
        return materials


@admin.register(RecruitmentSettings)
class RecruitmentSettingsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/portal/recruitmentsettings/change_list.html'
    list_display = ('current_state',)
    actions = None

    def get_urls(self):
        return [
            path('open/', self.admin_site.admin_view(self.set_open), name='portal_recruitment_open'),
            path('close/', self.admin_site.admin_view(self.set_closed), name='portal_recruitment_close'),
        ] + super().get_urls()

    def set_open(self, request):
        if request.method != 'POST': return HttpResponseNotAllowed(['POST'])
        settings = RecruitmentSettings.current(); settings.is_open = True; settings.save(update_fields=['is_open'])
        self.message_user(request, '已开启在线报名，前台现在可以提交。', messages.SUCCESS)
        return redirect('admin:portal_recruitmentsettings_changelist')

    def set_closed(self, request):
        if request.method != 'POST': return HttpResponseNotAllowed(['POST'])
        settings = RecruitmentSettings.current(); settings.is_open = False; settings.save(update_fields=['is_open'])
        self.message_user(request, '已关闭在线报名，前台仍展示表单，但不会接收提交。', messages.SUCCESS)
        return redirect('admin:portal_recruitmentsettings_changelist')

    @admin.display(description='当前状态')
    def current_state(self, obj):
        return '报名已开放' if obj.is_open else '报名未开放'

    def changelist_view(self, request, extra_context=None):
        setting = RecruitmentSettings.current()
        return TemplateResponse(request, self.change_list_template, {
            **self.admin_site.each_context(request),
            'title': '招新设置', 'setting': setting,
        })

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False


@admin.register(NewsRevision)
class NewsRevisionAdmin(admin.ModelAdmin):
    list_display = ('article', 'note', 'created_at'); readonly_fields = ('article', 'snapshot', 'note', 'created_at'); ordering = ('-created_at',)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False


admin.site.site_header = 'PRIME 官网运营中心'
admin.site.site_title = 'PRIME 运营后台'
admin.site.index_title = '内容发布与招新审核'
