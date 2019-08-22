# Generated by Django 2.1 on 2018-09-14 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0012_botuser_amount_of_referrals'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='size',
        ),
        migrations.AddField(
            model_name='botuser',
            name='configured',
            field=models.BooleanField(default=False, verbose_name='Spam configured'),
        ),
    ]
