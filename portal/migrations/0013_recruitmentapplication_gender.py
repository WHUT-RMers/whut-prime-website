# Generated manually for the public recruitment form gender field.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0012_recruitmentapplication_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitmentapplication',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', '男'), ('female', '女'), ('other', '其他/不便填写')], default='', max_length=16, verbose_name='性别'),
        ),
    ]
