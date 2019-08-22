# Generated by Django 2.1 on 2018-10-11 16:54

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0068_auto_20181010_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackdialogue',
            name='data',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='feedbackdialogue',
            name='last_message_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 11, 16, 54, 39, 372644, tzinfo=utc), verbose_name='Время последнего сообщения (часовой пояс UTC)'),
        ),
        migrations.AddField(
            model_name='feedbackdialogue',
            name='marked',
            field=models.BooleanField(default=False, verbose_name='Избранный'),
        ),
        migrations.AddField(
            model_name='feedbackdialogue',
            name='status',
            field=models.CharField(choices=[('open', 'Открыт'), ('closed', 'Закрыт'), ('ignored', 'Игнор')], default='open', max_length=7, verbose_name='Статус'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedbackdialogue',
            name='unread',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='postponedpost',
            name='image_place',
            field=models.CharField(choices=[('bottom', 'Снизу'), ('top', 'Сверху')], default='bottom', max_length=6, verbose_name='Расположение изображения'),
        ),
    ]
