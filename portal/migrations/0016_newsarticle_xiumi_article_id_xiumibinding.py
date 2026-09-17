from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0015_alter_recruitmentapplication_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='xiumi_article_id',
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=64,
                null=True,
                unique=True,
                verbose_name='秀米图文 ID',
            ),
        ),
        migrations.CreateModel(
            name='XiumiBinding',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('partner_user_id', models.CharField(max_length=120, unique=True, verbose_name='平台用户 ID')),
                ('open_id', models.CharField(max_length=120, unique=True, verbose_name='秀米用户 ID')),
                ('bind_name', models.CharField(blank=True, max_length=40, verbose_name='绑定名称')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='绑定时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '秀米绑定',
                'verbose_name_plural': '秀米绑定',
            },
        ),
    ]
