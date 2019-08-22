# Generated by Django 2.1 on 2018-09-27 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0038_auto_20180927_0857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postponedpost',
            name='offer_gender',
            field=models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский'), ('all', ' Мужской + Женский')], default='male', max_length=6, verbose_name='Пол'),
        ),
    ]
