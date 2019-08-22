# Generated by Django 2.1 on 2018-09-27 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0040_postponedpost_buttons'),
    ]

    operations = [
        migrations.AddField(
            model_name='postponedpost',
            name='offer_sizes_type',
            field=models.CharField(choices=[('EU', 'EU'), ('US', 'US'), ('UK', 'UK')], default='EU', max_length=2, verbose_name='Размерность'),
        ),
        migrations.AlterField(
            model_name='postponedpost',
            name='text',
            field=models.TextField(max_length=200, verbose_name='Текст (форматированный, 200 символов с учетом размеров обуви)'),
        ),
    ]
