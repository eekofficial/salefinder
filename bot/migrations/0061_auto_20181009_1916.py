# Generated by Django 2.1 on 2018-10-09 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0060_postponedpost_amount_of_receivers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postponedpost',
            name='amount_of_receivers',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество получивших пост пользователей'),
        ),
    ]
