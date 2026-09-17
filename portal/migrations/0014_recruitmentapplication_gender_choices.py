from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0013_recruitmentapplication_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruitmentapplication',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', '男'), ('female', '女')], default='', max_length=16, verbose_name='性别'),
        ),
    ]
