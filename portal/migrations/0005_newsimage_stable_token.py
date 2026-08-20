import uuid

import portal.models
from django.db import migrations, models
import django.db.models.deletion


def populate_image_tokens(apps, schema_editor):
    NewsImage = apps.get_model('portal', 'NewsImage')
    for image in NewsImage.objects.filter(token__isnull=True).iterator():
        image.token = uuid.uuid4()
        image.save(update_fields=['token'])


class Migration(migrations.Migration):
    dependencies = [('portal', '0004_move_legacy_body_images_into_article')]

    operations = [
        migrations.AlterField(
            model_name='newsimage',
            name='article',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='portal.newsarticle', verbose_name='所属资讯'),
        ),
        migrations.AddField(
            model_name='newsimage',
            name='token',
            field=models.UUIDField(editable=False, null=True, verbose_name='图片标识'),
        ),
        migrations.RunPython(populate_image_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='newsimage',
            name='token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='图片标识'),
        ),
        migrations.AlterField(
            model_name='newsimage',
            name='image',
            field=models.ImageField(upload_to=portal.models.news_upload_to, validators=[portal.models.validate_content_image], verbose_name='正文图片'),
        ),
    ]
