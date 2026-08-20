from html import escape

from django.db import migrations


def move_legacy_body_images(apps, schema_editor):
    """Keep existing body-image uploads visible after moving to inline rich text."""
    NewsArticle = apps.get_model('portal', 'NewsArticle')
    NewsImage = apps.get_model('portal', 'NewsImage')
    for article in NewsArticle.objects.all():
        body = article.body or ''
        additions = []
        for image in NewsImage.objects.filter(article_id=article.pk).order_by('sort_order', 'id'):
            url = f'/api/news/{article.slug}/images/{image.pk}/'
            if url in body:
                continue
            caption = escape(image.caption or '')
            caption_html = f'<figcaption>{caption}</figcaption>' if caption else ''
            additions.append(
                f'<figure class="news-inline-image"><img src="{url}" alt="{caption}">{caption_html}</figure>'
            )
        if additions:
            article.body = f'{body}\n' + '\n'.join(additions)
            article.save(update_fields=['body'])


class Migration(migrations.Migration):
    dependencies = [('portal', '0003_recruitmentapplication_contact_fields')]

    operations = [migrations.RunPython(move_legacy_body_images, migrations.RunPython.noop)]
