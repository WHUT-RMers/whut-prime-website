from pathlib import Path

from django.http import HttpResponse
from django.views.decorators.cache import never_cache

BASE_DIR = Path(__file__).resolve().parent.parent


@never_cache
def demo_page(request):
    """渲染 Vue 构建产物 index.html（静态资源由 /static/ 提供）。"""
    index = BASE_DIR / 'frontend' / 'dist' / 'index.html'
    try:
        html = index.read_text(encoding='utf-8')
    except FileNotFoundError:
        return HttpResponse(
            '前端尚未构建：请先在 frontend/ 目录执行 npm run build',
            status=404,
            content_type='text/plain; charset=utf-8',
        )
    return HttpResponse(html, content_type='text/html; charset=utf-8')
