# Generated by Django 2.1 on 2018-09-12 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(unique=True, verbose_name='Id')),
                ('first_name', models.CharField(max_length=256, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=256, verbose_name='Second name')),
                ('username', models.CharField(blank=True, max_length=256, verbose_name='Username')),
                ('gender', models.CharField(blank=True, choices=[('male', 'male'), ('female', 'female')], max_length=256, verbose_name='Gender')),
                ('size', models.IntegerField(blank=True, verbose_name='Size')),
            ],
        ),
    ]
