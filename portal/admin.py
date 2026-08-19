from __future__ import annotations

from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.db.models import Sum
from django.http import FileResponse, Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .forms import RichTextWidget
from .models import (NewsArticle, NewsCoverSlide, NewsImage, NewsRevision,
                     NewsView, RecruitmentApplication, RecruitmentSettings)


class NewsArticleAdminForm(forms.ModelForm):
    body = forms.CharField(label='文章正文', widget=RichTextWidget, help_text='使用上方按钮添加小标题、加粗和列表；不要粘贴带复杂样式的 Word 内容。')
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
            'cover': '上传一张主封面。支持 JPG/PNG/WebP，至少 1200×675，最大 8 MB。',
            'image_focus': '主体在照片哪里就选哪里，前台裁切时会优先保留该区域。',
            'is_pinned': '勾选后排在资讯列表最前。',
            'is_featured': '勾选后显示在官网首页“最新动态”。',
            'external_url': '若有公众号、B站等原文，填完整网址；没有则留空。',
            'status': '草稿不会公开；已发布立即公开；定时发布到指定时间自动公开；下线会从前台隐藏。',
        }


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


class NewsImageInline(ImagePreviewMixin, admin.TabularInline):
    model = NewsImage
    extra = 0
    fields = ('image_preview', 'image', 'caption', 'sort_order')
    readonly_fields = ('image_preview',)
    verbose_name = '正文图片'
    verbose_name_plural = '正文图片（按排序数字依次展示）'

    def preview_url(self, obj):
        return reverse('admin:portal_news_file', args=[obj.article_id, 'body', obj.pk])


class NewsCoverSlideInline(ImagePreviewMixin, admin.TabularInline):
    model = NewsCoverSlide
    extra = 0
    fields = ('image_preview', 'image', 'caption', 'sort_order')
    readonly_fields = ('image_preview',)
    verbose_name = '额外封面图'
    verbose_name_plural = '封面轮播图（可添加多张；前台会自动轮播）'

    def preview_url(self, obj):
        return reverse('admin:portal_news_file', args=[obj.article_id, 'slide', obj.pk])


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    form = NewsArticleAdminForm
    change_list_template = 'admin/portal/newsarticle/change_list.html'
    change_form_template = 'admin/portal/newsarticle/change_form.html'
    list_display = ('title', 'category', 'status', 'is_pinned', 'is_featured', 'published_at', 'view_count', 'views_7d', 'trash_state', 'recycle_button')
    list_filter = ('status', 'category', 'is_pinned', 'is_featured', 'is_trashed')
    search_fields = ('title', 'summary', 'body')
    readonly_fields = ('cover_preview', 'view_count', 'created_at', 'updated_at', 'metrics')
    # Do not use SimpleUI's inline list editing: it creates a misleading
    # "保存" button even though content publishing happens in the edit page.
    list_editable = ()
    inlines = (NewsCoverSlideInline, NewsImageInline)
    actions = None
    fieldsets = (
        ('① 文章内容', {'fields': ('title', 'slug', 'summary', 'category', 'body')}),
        ('② 封面与展示', {'fields': ('cover_preview', 'cover', 'image_focus', 'is_pinned', 'is_featured', 'external_url')}),
        ('③ 发布控制', {'fields': ('status', 'published_at')}),
        ('④ 数据与记录', {'fields': ('metrics', 'view_count', 'created_at', 'updated_at')}),
    )

    class Media:
        css = {'all': ('portal/admin_polish.css',)}
        js = ('portal/admin_images.js', 'portal/admin_bulk_actions.js')

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard), name='portal_news_dashboard'),
            path('<int:pk>/trash/', self.admin_site.admin_view(self.trash), name='portal_news_trash'),
            path('<int:pk>/restore/', self.admin_site.admin_view(self.restore), name='portal_news_restore'),
            path('<int:pk>/purge/', self.admin_site.admin_view(self.purge), name='portal_news_purge'),
            path('bulk/trash/', self.admin_site.admin_view(self.bulk_trash), name='portal_news_bulk_trash'),
            path('bulk/restore/', self.admin_site.admin_view(self.bulk_restore), name='portal_news_bulk_restore'),
            path('bulk/purge/', self.admin_site.admin_view(self.bulk_purge), name='portal_news_bulk_purge'),
            path('<int:pk>/file/<str:kind>/<int:item_id>/', self.admin_site.admin_view(self.news_file), name='portal_news_file'),
        ]
        return custom + urls

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
        super().save_model(request, obj, form, change)


@admin.register(RecruitmentApplication)
class RecruitmentApplicationAdmin(admin.ModelAdmin):
    form = RecruitmentApplicationAdminForm
    list_display = ('application_no', 'name', 'college', 'major_class', 'groups_display', 'status', 'created_at', 'resume_link')
    list_filter = ('status', 'created_at')
    search_fields = ('application_no', 'name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class')
    readonly_fields = ('application_no', 'created_at', 'updated_at', 'resume_link')
    list_editable = ('status',)
    fields = ('application_no', 'name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class', 'intended_groups', 'introduction', 'experience', 'availability', 'resume_link', 'status', 'interview_at', 'internal_note', 'created_at', 'updated_at')

    class Media:
        css = {'all': ('portal/admin_polish.css',)}

    @admin.display(description='意向组别')
    def groups_display(self, obj):
        mapping = dict(RecruitmentApplication.GROUPS)
        return '、'.join(mapping.get(key, key) for key in obj.intended_groups)

    @admin.display(description='简历')
    def resume_link(self, obj):
        if not obj.pk: return '保存后可下载'
        return format_html('<a href="{}">安全下载 PDF 简历</a>', reverse('portal:resume-download', args=[obj.pk]))


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
