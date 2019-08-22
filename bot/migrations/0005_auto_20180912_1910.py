# Generated by Django 2.1 on 2018-09-12 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_botuser_is_premium'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='is_premium',
        ),
        migrations.AddField(
            model_name='botuser',
            name='is_paid_premium',
            field=models.BooleanField(default=False, verbose_name='Is paid premium'),
        ),
    ]
