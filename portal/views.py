from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
import json
from django.db.models import F
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import RecruitmentApplicationForm
from .models import NewsArticle, NewsCoverSlide, NewsImage, NewsView, RecruitmentSettings


def image_response(file_field):
    if not file_field:
        raise Http404
    return FileResponse(file_field.open('rb'), content_type='image/*')


def article_data(article, request=None, detail=False):
    payload = {
        'slug': article.slug,
        'title': article.title,
        'summary': article.summary,
        'category': article.category,
        'cover_url': f'/api/news/{article.slug}/cover/',
        'cover_images': [{'id': 0, 'caption': '', 'url': f'/api/news/{article.slug}/cover/'}] + [
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
        payload['images'] = [
            {'id': image.id, 'caption': image.caption, 'url': f'/api/news/{article.slug}/images/{image.id}/'}
            for image in article.images.all()
        ]
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
def news_slide(request, slug, slide_id):
    article = get_object_or_404(NewsArticle.objects.live(), slug=slug)
    return image_response(get_object_or_404(NewsCoverSlide, pk=slide_id, article=article).image)


@require_GET
def recruitment_status(request):
    settings = RecruitmentSettings.current()
    return JsonResponse({'is_open': settings.is_open, 'notice': settings.notice})


@require_POST
def recruitment_submit(request):
    settings = RecruitmentSettings.current()
    if not settings.is_open:
        return JsonResponse({'error': '当前不在报名时间，暂不接收报名信息。'}, status=403)
    data = request.POST.copy()
    raw_groups = data.getlist('intended_groups')
    try:
        groups = json.loads(raw_groups[0]) if len(raw_groups) == 1 and raw_groups[0].startswith('[') else raw_groups
    except json.JSONDecodeError:
        groups = []
    data.setlist('intended_groups', groups if isinstance(groups, list) else [])
    form = RecruitmentApplicationForm(data, request.FILES)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)
    application = form.save()
    return JsonResponse({'application_no': application.application_no}, status=201)


@staff_member_required
def resume_download(request, pk):
    from .models import RecruitmentApplication
    application = get_object_or_404(RecruitmentApplication, pk=pk)
    return FileResponse(application.resume.open('rb'), as_attachment=True, filename=f'{application.application_no}-{application.name}.pdf')
