from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
import json
import mimetypes
import secrets
import io
import zipfile
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core import signing
from django.core.mail import send_mail
from django.core.cache import cache
from django.db.models import F
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_GET, require_POST

from .forms import RecruitmentApplicationForm
from .models import (NewsArticle, NewsCoverSlide, NewsImage, NewsView,
                     RecruitmentApplication,
                     RecruitmentEmailVerification, RecruitmentSettings)


EMAIL_CODE_SESSION_KEY = 'recruitment_verified_email'
EMAIL_CODE_TTL = timedelta(minutes=10)
EMAIL_CODE_RESEND_WAIT = timedelta(seconds=60)
EMAIL_CODE_DAILY_LIMIT = 5
EMAIL_CODE_IP_HOURLY_LIMIT = 10
EMAIL_VERIFY_SALT = 'whut-prime-recruit-email-verify'


def normalize_email(value: str) -> str:
    return value.strip().lower()


def email_verification_enabled() -> bool:
    return bool(settings.RECRUITMENT_EMAIL_VERIFICATION_ENABLED and settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)


def is_email_verified(email: str) -> bool:
    """链接点击后以数据库记录为准（不依赖会话），供表单页轮询与提交校验。"""
    record = RecruitmentEmailVerification.objects.filter(email=email).first()
    if not record or not record.verified_at:
        return False
    now = timezone.now()
    # verified_at 必须晚于最近一次发送，且仍在校验有效期内
    return record.verified_at >= record.last_sent_at and record.expires_at > now


def verify_page_html(message: str) -> str:
    """邮件链接落地页：极简自包含 HTML，无外部资源，不跳转回报名页。"""
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>邮箱验证 · WHUT PRIME</title></head>'
        '<body style="margin:0;min-height:100vh;display:grid;place-items:center;background:#07080d;'
        'color:#eef2f9;font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif;text-align:center">'
        '<div style="max-width:440px;margin:24px;padding:48px 30px;border:1px solid rgba(45,226,166,.35);'
        'border-radius:16px;background:#0c0e15">'
        '<div style="width:54px;height:54px;margin:0 auto 22px;border:2px solid #2de2a6;border-radius:50%;'
        'display:grid;place-items:center;color:#2de2a6;font-size:26px">&#10003;</div>'
        '<h1 style="margin:0;font-size:1.15rem;letter-spacing:.06em">邮箱验证</h1>'
        f'<p style="margin:14px 0 0;color:#97a3b6;font-size:.95rem;line-height:1.8">{message}</p>'
        '</div></body></html>'
    )


def check_email_code_ip_limit(request) -> bool:
    """A coarse request limit that still applies when a target address is invalid."""
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f'recruitment-email-code-ip:{ip}'
    count = int(cache.get(key, 0))
    if count >= EMAIL_CODE_IP_HOURLY_LIMIT:
        return False
    cache.set(key, count + 1, timeout=60 * 60)
    return True


def can_applicant_edit(application: RecruitmentApplication) -> bool:
    return (
        application.status == RecruitmentApplication.Status.PENDING
        and application.modification_count < 2
    )


def application_payload(application: RecruitmentApplication, include_form=False) -> dict:
    payload = {
        'id': application.pk, 'application_no': application.application_no,
        'primary_choice': application.primary_choice, 'status': application.get_status_display(),
        'created_at': timezone.localtime(application.created_at).strftime('%Y-%m-%d %H:%M'),
        'can_edit': can_applicant_edit(application),
        'modification_count': application.modification_count,
    }
    if include_form:
        payload['form'] = {
            field: getattr(application, field) for field in (
                'name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class',
                'primary_choice', 'accepts_adjustment', 'second_choice', 'introduction',
                'experience', 'availability', 'consent',
            )
        }
        payload['attachments'] = [attachment.original_name for attachment in application.attachments.all()]
    return payload


def form_error_message(form: RecruitmentApplicationForm) -> str:
    """Return a concise, user-facing summary while retaining structured errors."""
    messages = []
    for field_errors in form.errors.get_json_data().values():
        messages.extend(item['message'] for item in field_errors)
    return '；'.join(messages) or '提交信息不完整，请检查后重试。'


def image_response(file_field):
    if not file_field:
        raise Http404
    content_type = mimetypes.guess_type(file_field.name)[0] or 'application/octet-stream'
    return FileResponse(file_field.open('rb'), content_type=content_type)


def article_data(article, request=None, detail=False):
    payload = {
        'slug': article.slug,
        'title': article.title,
        'summary': article.summary,
        'category': article.category,
        'cover_url': f'/api/news/{article.slug}/cover/',
        'cover_images': [{'id': 0, 'caption': article.cover_caption, 'url': f'/api/news/{article.slug}/cover/'}] + [
            {'id': slide.id, 'caption': slide.caption, 'url': f'/api/news/{article.slug}/slides/{slide.id}/'}
            for slide in article.cover_slides.all()
        ],
        'image_focus': article.image_focus.replace('-', ' '),
        'published_at': article.published_at.isoformat() if article.published_at else None,
        'is_pinned': article.is_pinned,
        'external_url': article.external_url,
        'view_count': article.view_count,
    }
    if detail:
        payload['body'] = article.body
    return payload


@require_GET
def news_list(request):
    page_size = min(max(int(request.GET.get('limit', 12)), 1), 50)
    category = request.GET.get('category', '').strip()
    articles = NewsArticle.objects.live().prefetch_related('images', 'cover_slides')
    if category:
        articles = articles.filter(category=category)
    if request.GET.get('featured') == '1':
        articles = articles.filter(is_featured=True)
    items = list(articles[:page_size])
    # Remove the model's article ordering before DISTINCT; otherwise SQLite includes
    # ordering columns and can return one category more than once.
    categories = list(NewsArticle.objects.live().order_by('category').values_list('category', flat=True).distinct())
    return JsonResponse({'items': [article_data(article) for article in items], 'categories': categories})


@require_GET
def news_detail(request, slug):
    article = get_object_or_404(NewsArticle.objects.live().prefetch_related('images', 'cover_slides'), slug=slug)
    previous_article = NewsArticle.objects.live().filter(published_at__gt=article.published_at).order_by('published_at').first()
    next_article = NewsArticle.objects.live().filter(published_at__lt=article.published_at).order_by('-published_at').first()
    payload = article_data(article, request, detail=True)
    payload['previous'] = article_data(previous_article) if previous_article else None
    payload['next'] = article_data(next_article) if next_article else None
    return JsonResponse(payload)


@require_POST
def news_view(request, slug):
    article = get_object_or_404(NewsArticle.objects.live(), slug=slug)
    key = f'news-view:{article.pk}'
    last_seen = request.session.get(key)
    now = timezone.now().timestamp()
    if not last_seen or now - last_seen > 1800:
        request.session[key] = now
        NewsView.objects.create(article=article)
        NewsArticle.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)
        article.refresh_from_db(fields=['view_count'])
    return JsonResponse({'view_count': article.view_count})


@require_GET
def news_cover(request, slug):
    return image_response(get_object_or_404(NewsArticle.objects.live(), slug=slug).cover)


@require_GET
def news_image(request, slug, image_id):
    article = get_object_or_404(NewsArticle.objects.live(), slug=slug)
    return image_response(get_object_or_404(NewsImage, pk=image_id, article=article).image)


@require_GET
def news_content_image(request, token):
    image = get_object_or_404(NewsImage.objects.select_related('article'), token=token)
    # 后台编辑草稿时允许管理员预览；普通访客只能读取已公开资讯引用的图片。
    if not request.user.is_staff:
        if not image.article_id or not NewsArticle.objects.live().filter(pk=image.article_id).exists():
            raise Http404
    return image_response(image.image)


@require_GET
def news_slide(request, slug, slide_id):
    article = get_object_or_404(NewsArticle.objects.live(), slug=slug)
    return image_response(get_object_or_404(NewsCoverSlide, pk=slide_id, article=article).image)


@require_GET
def recruitment_status(request):
    settings = RecruitmentSettings.current()
    return JsonResponse({
        'is_open': settings.is_open,
        'notice': settings.notice,
        'email_verification_required': email_verification_enabled(),
    })


@require_POST
def recruitment_send_email_code(request):
    if not email_verification_enabled():
        return JsonResponse({'error': '邮箱验证码尚未配置，请稍后再试。'}, status=503)
    email = normalize_email(request.POST.get('email', ''))
    if not email or '@' not in email:
        return JsonResponse({'error': '请输入有效的邮箱地址。'}, status=400)
    if not check_email_code_ip_limit(request):
        return JsonResponse({'error': '操作过于频繁，请一小时后再试。'}, status=429)
    now = timezone.now()
    record = RecruitmentEmailVerification.objects.filter(email=email).first()
    today = timezone.localdate()
    if record and record.sent_on == today:
        if now - record.last_sent_at < EMAIL_CODE_RESEND_WAIT:
            seconds = int((EMAIL_CODE_RESEND_WAIT - (now - record.last_sent_at)).total_seconds()) + 1
            return JsonResponse({'error': f'请在 {seconds} 秒后再试。'}, status=429)
        if record.sent_count >= EMAIL_CODE_DAILY_LIMIT:
            return JsonResponse({'error': '该邮箱今日验证码发送次数已达上限，请明天再试。'}, status=429)
    code = f'{secrets.randbelow(1_000_000):06d}'
    defaults = {
        'code_hash': make_password(code), 'expires_at': now + EMAIL_CODE_TTL,
        'verified_at': None, 'last_sent_at': now,
        'sent_count': (record.sent_count + 1) if record and record.sent_on == today else 1,
        'sent_on': today, 'failed_attempts': 0,
    }
    # Record the attempt before talking to SMTP.  A mail failure must not let a
    # caller bypass the same-address cooldown by retrying immediately.
    RecruitmentEmailVerification.objects.update_or_create(email=email, defaults=defaults)
    # 邮件里只放一个签名魔法链接：点击即验证，无需回填验证码、无需跳转。
    token = signing.dumps({'email': email}, salt=EMAIL_VERIFY_SALT)
    link = request.build_absolute_uri(reverse('portal:recruitment-email-verify')) + '?token=' + token
    minutes = int(EMAIL_CODE_TTL.total_seconds() // 60)
    try:
        sent = send_mail(
            'PRIME 招新邮箱验证',
            (
                f'请点击以下链接完成邮箱验证（{minutes} 分钟内有效）：\n\n{link}\n\n'
                '点击链接后会自动完成验证，报名页面会同步变为「已验证」状态，无需跳转回来。\n'
                '若非本人操作，请忽略此邮件。'
            ),
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        if sent != 1:
            raise RuntimeError('SMTP did not accept the message')
    except Exception:
        return JsonResponse({
            'error': '验证码发送失败，请检查邮箱地址或稍后重试。',
            'cooldown_seconds': 60,
        }, status=502)
    return JsonResponse({'message': '验证链接已发送至报名邮箱，请查收邮件并点击链接完成验证。'})


@require_POST
def recruitment_email_status(request):
    """表单页轮询：链接被点击后由数据库记录判断是否已验证（不依赖会话/跳转）。"""
    email = normalize_email(request.POST.get('email', ''))
    return JsonResponse({'verified': is_email_verified(email) if email else False})


@require_GET
def recruitment_email_verify(request):
    """邮件魔法链接：点击即自动验证。无需重定向回报名页，表单页通过轮询同步状态。"""
    token = request.GET.get('token', '')
    try:
        payload = signing.loads(token, salt=EMAIL_VERIFY_SALT, max_age=EMAIL_CODE_TTL.total_seconds())
    except signing.BadSignature:
        return HttpResponse(verify_page_html('链接无效或已过期，请重新发送验证链接。'), status=400)
    email = normalize_email(str(payload.get('email') or ''))
    if not email or '@' not in email or not email_verification_enabled():
        return HttpResponse(verify_page_html('链接无效。'), status=400)
    now = timezone.now()
    record = RecruitmentEmailVerification.objects.filter(email=email).first()
    if record:
        record.verified_at = now
        record.failed_attempts = 0
        record.save(update_fields=['verified_at', 'failed_attempts'])
    else:
        RecruitmentEmailVerification.objects.create(
            email=email, code_hash=make_password(secrets.token_hex(8)),
            expires_at=now + EMAIL_CODE_TTL, verified_at=now, last_sent_at=now,
        )
    # 同一浏览器内顺手写入会话，兼容旧逻辑；跨端场景由轮询 + 数据库记录覆盖。
    request.session[EMAIL_CODE_SESSION_KEY] = email
    return HttpResponse(verify_page_html('邮箱验证成功，现在可以返回报名页面提交简历了。'))


@require_POST
def recruitment_application_status(request):
    email = normalize_email(request.POST.get('email', ''))
    if email_verification_enabled() and not is_email_verified(email):
        return JsonResponse({'error': '请先完成邮箱验证。'}, status=403)
    application = RecruitmentApplication.objects.filter(email__iexact=email).prefetch_related('attachments').order_by('-created_at').first()
    return JsonResponse({
        'exists': bool(application),
        'application': application_payload(application, include_form=True) if application else None,
    })


def recruitment_form_data(request):
    data = request.POST.copy()
    data['email'] = normalize_email(data.get('email', ''))
    raw_groups = data.getlist('intended_groups')
    try:
        groups = json.loads(raw_groups[0]) if len(raw_groups) == 1 and raw_groups[0].startswith('[') else raw_groups
    except json.JSONDecodeError:
        groups = []
    data.setlist('intended_groups', groups if isinstance(groups, list) else [])
    return data


@require_POST
def recruitment_submit(request):
    settings = RecruitmentSettings.current()
    if not settings.is_open:
        return JsonResponse({'error': '当前不在报名时间，暂不接收报名信息。'}, status=403)
    data = recruitment_form_data(request)
    email = data['email']
    if email_verification_enabled() and not is_email_verified(email):
        return JsonResponse({'error': '请先完成邮箱验证。'}, status=400)
    form = RecruitmentApplicationForm(data, request.FILES)
    if not form.is_valid():
        return JsonResponse({'error': form_error_message(form), 'errors': form.errors.get_json_data()}, status=400)
    application = form.save()
    application.email_verified = email_verification_enabled()
    application.save(update_fields=['email_verified'])
    request.session.pop(EMAIL_CODE_SESSION_KEY, None)
    return JsonResponse({'application_no': application.application_no}, status=201)


@require_POST
def recruitment_update(request, pk):
    application = get_object_or_404(RecruitmentApplication, pk=pk)
    data = recruitment_form_data(request)
    email = data['email']
    if email != normalize_email(application.email):
        return JsonResponse({'error': '请使用投递时验证过的邮箱进行修改。'}, status=403)
    if email_verification_enabled() and not is_email_verified(email):
        return JsonResponse({'error': '请先完成邮箱验证。'}, status=403)
    if not can_applicant_edit(application):
        return JsonResponse({'error': '此报名已进入处理流程，或修改次数已用完，暂不能在线修改。'}, status=403)
    form = RecruitmentApplicationForm(data, request.FILES, instance=application)
    if not form.is_valid():
        return JsonResponse({'error': form_error_message(form), 'errors': form.errors.get_json_data()}, status=400)
    application = form.save()
    application.modification_count += 1
    application.email_verified = True
    # 对报名者和后台而言，当前记录的提交时间就是最后一次有效提交时间。
    application.created_at = timezone.now()
    application.save(update_fields=['modification_count', 'email_verified', 'created_at', 'updated_at'])
    request.session.pop(EMAIL_CODE_SESSION_KEY, None)
    return JsonResponse({'application_no': application.application_no, 'message': '报名信息已更新。'})


@staff_member_required
def resume_download(request, pk):
    application = get_object_or_404(RecruitmentApplication.objects.prefetch_related('attachments'), pk=pk)
    materials = [(attachment.original_name, attachment.file) for attachment in application.attachments.all() if attachment.file]
    if not materials and application.resume:
        materials = [('简历.pdf', application.resume)]
    if not materials:
        raise Http404('该报名者没有上传附件。')
    archive_buffer = io.BytesIO()
    folder = f'{get_valid_filename(application.application_no)}_{get_valid_filename(application.name)}'
    with zipfile.ZipFile(archive_buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for original_name, file_field in materials:
            archive.writestr(f'{folder}/{get_valid_filename(original_name)}', file_field.read())
    archive_buffer.seek(0)
    return FileResponse(
        archive_buffer,
        as_attachment=True,
        filename=f'{application.application_no}-{application.name}-报名材料.zip',
        content_type='application/zip',
    )
