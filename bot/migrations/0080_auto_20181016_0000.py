# Generated by Django 2.1 on 2018-10-16 00:00

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0079_auto_20181016_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackdialogue',
            name='last_message_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 16, 0, 0, 34, 2086, tzinfo=utc), verbose_name='Время последнего сообщения (часовой пояс UTC)'),
        ),
    ]
