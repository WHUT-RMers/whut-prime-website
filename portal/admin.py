from __future__ import annotations

import json
import io
import mimetypes
import zipfile
from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.http import FileResponse, Http404, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.text import get_valid_filename

from .forms import CarouselImageField, RichTextWidget
from .models import (NewsArticle, NewsCoverSlide, NewsImage, NewsRevision,
                     NewsView, RecruitmentApplication, RecruitmentAttachment, RecruitmentSettings)


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
        ]
        return custom + urls

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
    list_display = ('application_no', 'name', 'college', 'major_class', 'primary_group_display', 'adjustment_display', 'status', 'created_at', 'resume_link')
    list_filter = ('primary_choice', 'status', 'accepts_adjustment', 'created_at')
    search_fields = ('application_no', 'name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class')
    readonly_fields = ('application_no', 'created_at', 'updated_at', 'resume_link', 'attachments_display')
    list_editable = ('status',)
    fields = ('application_no', 'name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class', 'primary_choice', 'accepts_adjustment', 'second_choice', 'introduction', 'experience', 'availability', 'resume_link', 'attachments_display', 'status', 'interview_at', 'internal_note', 'created_at', 'updated_at')

    class Media:
        css = {'all': ('portal/admin_polish.css',)}
        js = ('portal/recruitment_material_preview.js',)

    def get_urls(self):
        return [
            path('export-filtered/', self.admin_site.admin_view(self.export_filtered), name='portal_recruitment_export_filtered'),
            path('export-all/', self.admin_site.admin_view(self.export_all), name='portal_recruitment_export_all'),
            path('<int:pk>/resume-preview/', self.admin_site.admin_view(self.resume_preview), name='portal_recruitment_resume_preview'),
            path('<int:pk>/attachment/<int:attachment_id>/', self.admin_site.admin_view(self.attachment_file), name='portal_recruitment_attachment_file'),
            path('<int:pk>/attachment/<int:attachment_id>/preview-data/', self.admin_site.admin_view(self.attachment_preview_data), name='portal_recruitment_attachment_preview_data'),
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
        applications = RecruitmentApplication.objects.prefetch_related('attachments').all()
        primary = request.GET.get('primary_choice')
        status = request.GET.get('status')
        if primary:
            applications = applications.filter(primary_choice=primary)
        if status:
            applications = applications.filter(status=status)
        adjustment = request.GET.get('accepts_adjustment')
        if adjustment in {'0', '1'}:
            applications = applications.filter(accepts_adjustment=adjustment == '1')
        return applications

    def _export_archive(self, applications, filename, grouped=False):
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill

        groups = dict(RecruitmentApplication.GROUPS)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = '报名汇总'
            headers = ['报名编号', '姓名', '第一志愿', '服从调剂', '第二志愿/统筹', '审核状态', '学院', '专业与班级', 'QQ', '微信', '邮箱', '手机', '每周投入', '自我介绍', '项目/竞赛经历', '报名时间', '附件数量']
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
                    sheet.append([application.application_no, application.name, groups.get(application.primary_choice, application.primary_choice), '是' if application.accepts_adjustment else '否', second, application.get_status_display(), application.college, application.major_class, application.qq, application.wechat, application.email, application.phone, application.availability, application.introduction, application.experience, application.created_at.replace(tzinfo=None), application.attachments.count()])
                    row += 1
                    folder_group = groups.get(application.primary_choice, application.primary_choice) if grouped else '报名材料'
                    folder = f'{folder_group}/{get_valid_filename(application.application_no)}_{get_valid_filename(application.name)}'
                    for attachment in application.attachments.all():
                        if attachment.file:
                            archive.writestr(f'{folder}/{get_valid_filename(attachment.original_name)}', attachment.file.read())
                row += 1 if grouped else 0
            sheet.freeze_panes = 'A2'
            for column, width in {'A':18,'B':12,'C':12,'D':12,'E':18,'F':12,'G':18,'H':28,'I':14,'J':18,'K':28,'L':16,'M':16,'N':38,'O':38,'P':20,'Q':12}.items():
                sheet.column_dimensions[column].width = width
            xlsx = io.BytesIO(); workbook.save(xlsx)
            archive.writestr('报名信息.xlsx', xlsx.getvalue())
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=filename)

    def export_filtered(self, request):
        return self._export_archive(self._filtered_applications(request), 'PRIME-筛选报名导出.zip')

    def export_all(self, request):
        return self._export_archive(RecruitmentApplication.objects.prefetch_related('attachments').all(), 'PRIME-全部报名归档.zip', grouped=True)

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

    def attachment_preview_data(self, request, pk, attachment_id):
        """Extract a safe, lightweight preview for office documents and ZIP archives."""
        attachment = get_object_or_404(RecruitmentAttachment, pk=attachment_id, application_id=pk)
        suffix = attachment.original_name.rsplit('.', 1)[-1].lower() if '.' in attachment.original_name else ''
        try:
            with attachment.file.open('rb') as uploaded:
                content = uploaded.read()
            if suffix == 'docx':
                from docx import Document
                document = Document(io.BytesIO(content))
                paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
                return JsonResponse({'kind': 'document', 'title': attachment.original_name, 'paragraphs': paragraphs[:160]})
            if suffix == 'xlsx':
                from openpyxl import load_workbook
                workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
                sheets = []
                for worksheet in list(workbook.worksheets)[:6]:
                    rows = []
                    for values in worksheet.iter_rows(max_row=80, max_col=20, values_only=True):
                        rows.append(['' if value is None else str(value)[:240] for value in values])
                    sheets.append({'name': worksheet.title, 'rows': rows})
                return JsonResponse({'kind': 'spreadsheet', 'title': attachment.original_name, 'sheets': sheets})
            if suffix == 'pptx':
                from pptx import Presentation
                presentation = Presentation(io.BytesIO(content))
                slides = []
                for number, slide in enumerate(presentation.slides, start=1):
                    texts = [shape.text.strip() for shape in slide.shapes if getattr(shape, 'has_text_frame', False) and shape.text.strip()]
                    slides.append({'number': number, 'text': texts[:20]})
                return JsonResponse({'kind': 'presentation', 'title': attachment.original_name, 'slides': slides})
            if suffix == 'zip':
                with zipfile.ZipFile(io.BytesIO(content)) as archive:
                    names = [info.filename for info in archive.infolist() if not info.is_dir()]
                return JsonResponse({'kind': 'archive', 'title': attachment.original_name, 'files': names[:300], 'total': len(names)})
        except Exception:
            return JsonResponse({'kind': 'unsupported', 'title': attachment.original_name, 'message': '此文件无法生成在线预览，请下载后使用对应软件打开。'})
        return JsonResponse({'kind': 'unsupported', 'title': attachment.original_name, 'message': '此格式暂不支持在线预览，请下载后使用对应软件打开。'})

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
            '<a class="recruitment-download-link" href="{}">下载附件</a>'
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
                })
        if not materials and obj.resume:
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
