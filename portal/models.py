from __future__ import annotations

import os
import uuid
from datetime import timedelta

from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def news_upload_to(instance, filename: str) -> str:
    return f'news/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{os.path.splitext(filename)[1].lower()}'


def resume_upload_to(instance, filename: str) -> str:
    return f'private/resumes/{timezone.now():%Y/%m}/{uuid.uuid4().hex}.pdf'


def recruitment_attachment_upload_to(instance, filename: str) -> str:
    return f'private/recruitment_attachments/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{os.path.splitext(filename)[1].lower()}'


def validate_image(value) -> None:
    if not value:
        return
    if value.size > 8 * 1024 * 1024:
        raise ValidationError('图片不能超过 8 MB。')
    try:
        value.open('rb')
        with Image.open(value.file) as image:
            width, height = image.size
    except (FileNotFoundError, UnidentifiedImageError, OSError) as error:
        raise ValidationError('无法读取图片，请重新上传 JPG、PNG 或 WebP 图片。') from error
    finally:
        try:
            value.seek(0)
        except (AttributeError, OSError):
            pass
    if width < 1200 or height < 675:
        raise ValidationError('图片至少需要 1200 × 675 像素，才能保证官网展示清晰。')


def validate_content_image(value) -> None:
    """正文插图允许横图或竖图，但仍保证官网阅读时足够清晰。"""
    if not value:
        return
    if value.size > 8 * 1024 * 1024:
        raise ValidationError('正文图片不能超过 8 MB。')
    try:
        value.open('rb')
        with Image.open(value.file) as image:
            width, height = image.size
    except (FileNotFoundError, UnidentifiedImageError, OSError) as error:
        raise ValidationError('无法读取图片，请重新上传 JPG、PNG 或 WebP 图片。') from error
    finally:
        try:
            value.seek(0)
        except (AttributeError, OSError):
            pass
    if width < 800 or height < 450:
        raise ValidationError('正文图片至少需要 800 × 450 像素。')


def validate_resume(value) -> None:
    if value.size > 10 * 1024 * 1024:
        raise ValidationError('简历不能超过 10 MB。')
    if not value.name.lower().endswith('.pdf') or getattr(value, 'content_type', '') not in ('application/pdf', ''):
        raise ValidationError('请上传 PDF 格式的简历。')


def validate_recruitment_attachment(value) -> None:
    if value.size > 15 * 1024 * 1024:
        raise ValidationError('单个附件不能超过 15 MB。')
    allowed = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
        '.txt', '.md', '.csv', '.json',
        '.mp4', '.mov', '.webm', '.mp3', '.wav', '.m4a',
        '.zip', '.rar', '.7z',
    }
    if os.path.splitext(value.name)[1].lower() not in allowed:
        raise ValidationError('附件支持常见文档、表格、演示、图片、音视频、文本和压缩包格式。')


class NewsArticleQuerySet(models.QuerySet):
    def live(self):
        now = timezone.now()
        return self.filter(is_trashed=False).filter(
            models.Q(status=NewsArticle.Status.PUBLISHED) |
            models.Q(status=NewsArticle.Status.SCHEDULED, published_at__lte=now)
        )


class NewsArticle(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PUBLISHED = 'published', '已发布'
        SCHEDULED = 'scheduled', '定时发布'
        OFFLINE = 'offline', '已下线'

    class Focus(models.TextChoices):
        CENTER = 'center', '居中'
        TOP = 'top', '顶部'
        BOTTOM = 'bottom', '底部'
        LEFT = 'left', '左侧'
        RIGHT = 'right', '右侧'

    title = models.CharField('标题', max_length=120)
    slug = models.SlugField('链接别名', max_length=150, unique=True, blank=True, allow_unicode=True)
    summary = models.CharField('摘要', max_length=240)
    category = models.CharField('分类', max_length=32)
    body = models.TextField('正文')
    cover = models.ImageField('封面图', upload_to=news_upload_to, validators=[validate_image])
    cover_caption = models.CharField('首张封面说明', max_length=160, blank=True)
    image_focus = models.CharField('图片焦点', max_length=10, choices=Focus.choices, default=Focus.CENTER)
    status = models.CharField('状态', max_length=12, choices=Status.choices, default=Status.DRAFT)
    is_pinned = models.BooleanField('置顶', default=False)
    is_featured = models.BooleanField('首页推荐', default=False)
    external_url = models.URLField('原文链接', blank=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    is_trashed = models.BooleanField('已移入回收站', default=False)
    view_count = models.PositiveIntegerField('总浏览量', default=0, editable=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    objects = NewsArticleQuerySet.as_manager()

    class Meta:
        verbose_name = '战队资讯'
        verbose_name_plural = '战队资讯'
        ordering = ('-is_pinned', '-published_at', '-created_at')

    def __str__(self) -> str:
        return self.title

    def clean(self):
        if self.status in (self.Status.PUBLISHED, self.Status.SCHEDULED) and not self.published_at:
            raise ValidationError({'published_at': '发布或定时发布时，请设置发布时间。'})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)[:135] or uuid.uuid4().hex[:12]
            candidate, index = base, 2
            while NewsArticle.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
                candidate = f'{base}-{index}'
                index += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def views_7d(self):
        return self.views.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()

    @property
    def views_30d(self):
        return self.views.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()


class NewsImage(models.Model):
    article = models.ForeignKey(NewsArticle, verbose_name='所属资讯', related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    token = models.UUIDField('图片标识', default=uuid.uuid4, unique=True, editable=False)
    image = models.ImageField('正文图片', upload_to=news_upload_to, validators=[validate_content_image])
    caption = models.CharField('图片说明', max_length=160, blank=True)
    sort_order = models.PositiveSmallIntegerField('排序', default=0)

    class Meta:
        verbose_name = '正文图片'
        verbose_name_plural = '正文图片'
        ordering = ('sort_order', 'id')

    def __str__(self):
        return self.caption or f'正文图片 #{self.pk or "新"}'


class NewsCoverSlide(models.Model):
    """Additional cover images shown as a calm carousel on the article page."""
    article = models.ForeignKey(NewsArticle, verbose_name='所属资讯', related_name='cover_slides', on_delete=models.CASCADE)
    image = models.ImageField('轮播封面', upload_to=news_upload_to, validators=[validate_image])
    caption = models.CharField('图片说明', max_length=160, blank=True)
    sort_order = models.PositiveSmallIntegerField('排序', default=0)

    class Meta:
        verbose_name = '封面轮播图'
        verbose_name_plural = '封面轮播图'
        ordering = ('sort_order', 'id')

    def __str__(self):
        return self.caption or f'封面轮播图 #{self.pk or "新"}'


class NewsView(models.Model):
    article = models.ForeignKey(NewsArticle, related_name='views', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['article', 'created_at'])]


class NewsRevision(models.Model):
    article = models.ForeignKey(NewsArticle, verbose_name='资讯', related_name='revisions', on_delete=models.CASCADE)
    snapshot = models.JSONField('内容快照')
    note = models.CharField('操作说明', max_length=80, default='保存修改')
    created_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        verbose_name = '资讯修改记录'
        verbose_name_plural = '资讯修改记录'
        ordering = ('-created_at',)


class RecruitmentSettings(models.Model):
    is_open = models.BooleanField('开放在线报名', default=False)
    notice = models.CharField('报名提示', max_length=240, blank=True, default='招新暂未开放，请关注战队最新资讯。')

    class Meta:
        verbose_name = '招新设置'
        verbose_name_plural = '招新设置'

    def __str__(self):
        return '招新设置'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class RecruitmentApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '待审核'
        SCREENED = 'screened', '初筛通过'
        INTERVIEW = 'interview', '待面试'
        ACCEPTED = 'accepted', '已录取'
        REJECTED = 'rejected', '未通过'
        TALENT_POOL = 'talent_pool', '人才库'

    GROUPS = [('mechanical', '机械组'), ('electrical', '电控组'), ('algorithm', '算法组'), ('operations', '运营组')]

    application_no = models.CharField('报名编号', max_length=20, unique=True, editable=False)
    name = models.CharField('姓名', max_length=32)
    qq = models.CharField('QQ', max_length=20, default='')
    wechat = models.CharField('微信', max_length=80, default='')
    email = models.EmailField('邮箱', max_length=254, default='')
    email_verified = models.BooleanField('邮箱已验证', default=False, editable=False)
    modification_count = models.PositiveSmallIntegerField('报名者修改次数', default=0, editable=False)
    phone = models.CharField('手机号码', max_length=32, default='')
    college = models.CharField('学院', max_length=80)
    major_class = models.CharField('专业与班级', max_length=120, default='')
    # 保留早期字段，确保已有测试报名数据不会丢失；新报名统一使用“专业与班级”。
    contact = models.CharField('旧联系方式', max_length=80, blank=True, default='')
    major = models.CharField('旧专业', max_length=80, blank=True, default='')
    grade = models.CharField('旧年级', max_length=32, blank=True, default='')
    intended_groups = models.JSONField('意向组别')
    primary_choice = models.CharField('第一志愿', max_length=16, choices=GROUPS, default='mechanical')
    accepts_adjustment = models.BooleanField('服从组别调剂', default=False)
    second_choice = models.CharField('第二志愿', max_length=16, choices=GROUPS, blank=True)
    introduction = models.TextField('自我介绍')
    experience = models.TextField('项目/竞赛经历', blank=True)
    availability = models.CharField('每周可投入时间', max_length=80)
    resume = models.FileField('PDF 简历', upload_to=resume_upload_to, validators=[FileExtensionValidator(['pdf']), validate_resume])
    consent = models.BooleanField('已同意个人信息使用')
    status = models.CharField('审核状态', max_length=16, choices=Status.choices, default=Status.PENDING)
    internal_note = models.TextField('内部备注', blank=True)
    interview_at = models.DateTimeField('面试时间', null=True, blank=True)
    created_at = models.DateTimeField('报名时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '招新报名'
        verbose_name_plural = '招新报名'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.application_no} · {self.name}'

    def save(self, *args, **kwargs):
        if not self.application_no:
            self.application_no = f'PR{timezone.now():%y%m%d}{uuid.uuid4().hex[:5].upper()}'
        super().save(*args, **kwargs)


class RecruitmentEmailVerification(models.Model):
    """Short-lived email code state; the code itself is stored only as a hash."""
    email = models.EmailField('邮箱', max_length=254, unique=True)
    code_hash = models.CharField('验证码哈希', max_length=128)
    expires_at = models.DateTimeField('过期时间')
    verified_at = models.DateTimeField('验证时间', null=True, blank=True)
    last_sent_at = models.DateTimeField('最近发送时间')
    sent_count = models.PositiveSmallIntegerField('当日发送次数', default=1)
    sent_on = models.DateField('发送日期', default=timezone.localdate)
    failed_attempts = models.PositiveSmallIntegerField('错误尝试次数', default=0)

    class Meta:
        verbose_name = '招新邮箱验证码'
        verbose_name_plural = '招新邮箱验证码'


class RecruitmentApplicationRevision(models.Model):
    application = models.ForeignKey(RecruitmentApplication, related_name='applicant_revisions', on_delete=models.CASCADE)
    snapshot = models.JSONField('修改前内容')
    created_at = models.DateTimeField('修改时间', auto_now_add=True)

    class Meta:
        verbose_name = '报名者修改记录'
        verbose_name_plural = '报名者修改记录'
        ordering = ('-created_at',)


class RecruitmentAttachment(models.Model):
    application = models.ForeignKey(RecruitmentApplication, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField('报名附件', upload_to=recruitment_attachment_upload_to, validators=[validate_recruitment_attachment])
    original_name = models.CharField('原始文件名', max_length=255)
    created_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        verbose_name = '报名附件'
        verbose_name_plural = '报名附件'

    def __str__(self):
        return self.original_name
