from datetime import datetime, timedelta, timezone, date
from string import ascii_lowercase
from random import choice

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings

from preferences.models import Preferences

from telebot import TeleBot, types


class Statistics(Preferences):
    def total_users(self):
        return BotUser.objects.filter(deleted=False).count()
    total_users.short_description = 'Общее количество человек'
    def total_configured_users(self):
        return BotUser.objects.filter(deleted=False, configured=True).count()
    total_configured_users.short_description = 'Общее количество подписанных человек'

    def total_men(self):
        return BotUser.objects.filter(deleted=False, gender='male').count()
    total_men.short_description = 'Количество'

    def total_women(self):
        return BotUser.objects.filter(deleted=False, gender='female').count()
    total_women.short_description = 'Количество'

    @classmethod
    def count_size(cls, gender, size):
        size = str(size)
        users = BotUser.objects.filter(configured=True, gender='male' if gender == 'men' else 'female')
        return len([user for user in users
            if size in (user.sizes or '').split()
        ])

    def total_referrals(self):
        return BotUser.objects.aggregate(models.Sum('amount_of_referrals'))['amount_of_referrals__sum'] or 0
    total_referrals.short_description = 'Общее количество приглашенных человек'
    def total_referrals_amount_1(self):
        return BotUser.objects.filter(deleted=False, amount_of_referrals=1).count()
    total_referrals_amount_1.short_description = 'Пригласили 1 человека'
    def total_referrals_amount_2(self):
        return BotUser.objects.filter(deleted=False, amount_of_referrals=2).count()
    total_referrals_amount_2.short_description = 'Пригласили 2 человек'
    def total_referrals_amount_3(self):
        return BotUser.objects.filter(deleted=False, amount_of_referrals__gte=3).count()
    total_referrals_amount_3.short_description = 'Пригласили 3 и более человек'

    def day_clicks_referral_program(self):
        return Click.objects.filter(button='referral_program', time__gte=datetime.now(timezone.utc) - timedelta(1)).count()
    def month_clicks_referral_program(self):
        return Click.objects.filter(button='referral_program', time__gte=datetime.now(timezone.utc) - timedelta(30)).count()
    def all_clicks_referral_program(self):
        return Click.objects.filter(button='referral_program').count()
    day_clicks_referral_program.short_description = \
    month_clicks_referral_program.short_description = \
    all_clicks_referral_program.short_description = 'Реферальная программа'

    def day_clicks_rating(self):
        return Click.objects.filter(button='rating', time__gte=datetime.now(timezone.utc) - timedelta(1)).count()
    def month_clicks_rating(self):
        return Click.objects.filter(button='rating', time__gte=datetime.now(timezone.utc) - timedelta(30)).count()
    def all_clicks_rating(self):
        return Click.objects.filter(button='rating').count()
    day_clicks_rating.short_description = \
    month_clicks_rating.short_description = \
    all_clicks_rating.short_description = 'Рейтинг'

    def day_clicks_invite(self):
        return Click.objects.filter(button='invite', time__gte=datetime.now(timezone.utc) - timedelta(1)).count()
    def month_clicks_invite(self):
        return Click.objects.filter(button='invite', time__gte=datetime.now(timezone.utc) - timedelta(30)).count()
    def all_clicks_invite(self):
        return Click.objects.filter(button='invite').count()
    day_clicks_invite.short_description = \
    month_clicks_invite.short_description = \
    all_clicks_invite.short_description = 'Пригласить друга'

    def day_clicks_premium(self):
        return Click.objects.filter(button='premium', time__gte=datetime.now(timezone.utc) - timedelta(1)).count()
    def month_clicks_premium(self):
        return Click.objects.filter(button='premium', time__gte=datetime.now(timezone.utc) - timedelta(30)).count()
    def all_clicks_premium(self):
        return Click.objects.filter(button='premium').count()
    day_clicks_premium.short_description = \
    month_clicks_premium.short_description = \
    all_clicks_premium.short_description = 'Премиум скидки'

    def day_clicks_setup_spam(self):
        return Click.objects.filter(button='setup_spam', time__gte=datetime.now(timezone.utc) - timedelta(1)).count()
    def month_clicks_setup_spam(self):
        return Click.objects.filter(button='setup_spam', time__gte=datetime.now(timezone.utc) - timedelta(30)).count()
    def all_clicks_setup_spam(self):
        return Click.objects.filter(button='setup_spam').count()
    day_clicks_setup_spam.short_description = \
    month_clicks_setup_spam.short_description = \
    all_clicks_setup_spam.short_description = 'Настройка рассылки'

    def day_clicks_callback(self):
        return Click.objects.filter(button='callback', time__gte=datetime.now(timezone.utc) - timedelta(1)).count()
    def month_clicks_callback(self):
        return Click.objects.filter(button='callback', time__gte=datetime.now(timezone.utc) - timedelta(30)).count()
    def all_clicks_callback(self):
        return Click.objects.filter(button='callback').count()
    day_clicks_callback.short_description = \
    month_clicks_callback.short_description = \
    all_clicks_callback.short_description = 'Обратная связь'

    class Meta:
        verbose_name = 'Просмотр'
        verbose_name_plural = 'Статистика'

    def __str__(self):
        return 'Просмотр'


class BotUser(models.Model):
    created = models.DateTimeField(
        verbose_name='Первый запуск бота (часовой пояс UTC)',
        auto_now_add=True
    )

    user_id = models.BigIntegerField(
        verbose_name='ID',
        unique=True
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=256
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=256,
        blank=True,
        null=True
    )

    username = models.CharField(
        verbose_name='Логин',
        max_length=256,
        blank=True,
        null=True
    )

    inviter_id = models.BigIntegerField(
        verbose_name='ID пригласителя',
        blank=True,
        null=True
    )
    amount_of_referrals = models.IntegerField(
        verbose_name='Количество приглашенных',
        default=0
    )

    def is_premium(self):
        return self.is_paid_premium or self.is_referral_premium()
    is_premium.boolean = True
    is_premium.short_description = 'Премиум аккаунт'
    is_paid_premium = models.BooleanField(
        verbose_name='Платный премиум аккаунт',
        default=False
    )
    def is_referral_premium(self):
        return self.amount_of_referrals >= 3
    is_referral_premium.boolean = True
    is_referral_premium.short_description = '3 или более рефералов'

    gender = models.CharField(
        verbose_name='Пол',
        max_length=256,
        choices=[
            ('male', 'Мужской'),
            ('female', 'Женский')
        ],
        blank=True,
        null=True
    )
    def float_sizes(self):
        return [float(size) for size in (self.sizes or '').split()]
    sizes = models.CharField(
        verbose_name='Размеры',
        max_length=1024,
        blank=True,
        null=True
    )
    configured = models.BooleanField(
        verbose_name='Рассылка настроена',
        default=False
    )

    last_setup_spam_message_id = models.BigIntegerField(
        blank=True,
        null=True
    )
    setup_spam_checked_sizes = models.CharField(
        max_length=1024,
        blank=True,
        null=True
    )
    last_referral_program_message_id = models.BigIntegerField(
        blank=True,
        null=True
    )
    last_premium_discounts_message_id = models.BigIntegerField(
        blank=True,
        null=True
    )
    last_premium_discounts_invoice_id = models.BigIntegerField(
        blank=True,
        null=True
    )

    last_messages_time = models.CharField(
        max_length=1024,
        blank=True,
        null=True
    )
    last_flood_message_time = models.FloatField(
        blank=True,
        null=True
    )

    feedback_enabled = models.BooleanField(
        default=False
    )

    deleted = models.BooleanField(
        verbose_name='Пользователь отписался от бота',
        default=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.user_id) + ('' if not self.username else f' - {self.username}')


class Click(models.Model):
    time = models.DateTimeField(
        auto_now_add=True
    )

    button = models.CharField(
        max_length=16,
        choices=[
            ('referral_program', 'referral_program'),
            ('rating', 'rating'),
            ('invite', 'invite'),
            ('premium', 'premium'),
            ('setup_spam', 'setup_spam'),
            ('callback', 'callback')
        ]
    )

    def __str__(self):
        return self.button


class Staff(models.Model):
    login = models.CharField(
        verbose_name='Логин',
        max_length=256,
        unique=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=256
    )

    base = models.OneToOneField(
        User,
        related_name='staff_data',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    content_management_rights = models.BooleanField(
        verbose_name='Менеджмент контента'
    )
    support_rights = models.BooleanField(
        verbose_name='Поддержка'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.base = User.objects.create_user(
                username=self.login,
                password=self.password,
                is_staff=True,
                is_superuser=True
            )

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.login


@receiver(pre_delete, sender=Staff)
def delete_related_base_user(sender, instance, *args, **kwargs):
    instance.base.delete()


class PostponedPost(models.Model):
    created = models.DateTimeField(
        verbose_name='Дата создания (часовой пояс UTC)',
        auto_now_add=True
    )
    sent = models.DateField(
        default=date(2040, 1, 1)
    )
    amount_of_receivers = models.IntegerField(
        verbose_name='Количество получивших пост пользователей',
        blank=True,
        null=True
    )

    type = models.CharField(
        verbose_name='Тип публикации',
        max_length=5,
        choices=[
            ('post', 'Пост'),
            ('offer', 'Оффер')
        ]
    )

    status = models.CharField(
        verbose_name='Статус',
        max_length=9,
        choices=[
            ('postponed', 'Отложен'),
            ('queue', 'В очереди'),
            ('process', 'Рассылается'),
            ('done', 'Разослан')
        ],
        blank=True,
        null=True
    )

    def validate_image(image):
        filesize = image.file.size
        limit_mb = 1
        if filesize > limit_mb * 1024 * 1024:
            raise ValidationError(f'Максимальный размер файла - {limit_mb}МБ')

    def get_image_path(instance, filename):
        length = 8
        path = ''
        for index in range(length):
            path += choice(ascii_lowercase)
        return path + '.' + filename.split('.')[-1]
    image = models.ImageField(
        verbose_name='Изображение (до 1МБ)',
        upload_to=get_image_path,
        blank=True,
        null=True,
        validators=[validate_image]
    )
    image_place = models.CharField(
        verbose_name='Расположение изображения',
        max_length=6,
        choices=[
            ('bottom', 'Снизу'),
            # ('top', 'Сверху')
        ],
        default='bottom'
    )

    draft = models.ForeignKey(
        verbose_name='Черновик',
        to='Draft',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    text = models.TextField(
        verbose_name='Текст (форматированный, 200 символов для постов с картинкой сверху)',
        max_length=5000
    )

    amount_of_buttons = models.IntegerField(
        verbose_name='Количество кнопок-ссылок',
        choices=[
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4)
        ],
        default=0
    )
    button_1_title = models.CharField(
        verbose_name='Текст 1-й кнопки',
        max_length=100,
        blank=True,
        null=True
    )
    button_1_link = models.URLField(
        verbose_name='Ссылка 1-й кнопки',
        blank=True,
        null=True
    )
    button_2_title = models.CharField(
        verbose_name='Текст 2-й кнопки',
        max_length=100,
        blank=True,
        null=True
    )
    button_2_link = models.URLField(
        verbose_name='Ссылка 2-й кнопки',
        blank=True,
        null=True
    )
    button_3_title = models.CharField(
        verbose_name='Текст 3-й кнопки',
        max_length=100,
        blank=True,
        null=True
    )
    button_3_link = models.URLField(
        verbose_name='Ссылка 3-й кнопки',
        blank=True,
        null=True
    )
    button_4_title = models.CharField(
        verbose_name='Текст 4-й кнопки',
        max_length=100,
        blank=True,
        null=True
    )
    button_4_link = models.URLField(
        verbose_name='Ссылка 4-й кнопки',
        blank=True,
        null=True
    )

    post_all = models.BooleanField(
        verbose_name='Все пользователи',
        default=True
    )
    post_need_spam_setup = models.BooleanField(
        verbose_name='Кто не настроил рассылку',
        default=False
    )
    post_0_referrals = models.BooleanField(
        verbose_name='У кого 0 рефералов',
        default=False
    )
    post_1_referrals = models.BooleanField(
        verbose_name='У кого 1 рефералов',
        default=False
    )
    post_2_referrals = models.BooleanField(
        verbose_name='У кого 2 рефералов',
        default=False
    )
    post_3_and_more_referrals = models.BooleanField(
        verbose_name='У кого 3 и более рефералов',
        default=False
    )

    offer_gender = models.CharField(
        verbose_name='Пол',
        max_length=6,
        choices=[
            ('male', 'Мужской'),
            ('female', 'Женский'),
            ('all', ' Мужской + Женский'),
        ],
        default='male'
    )
    offer_sizes_type = models.CharField(
        verbose_name='Размерность (которая отображается пользователям)',
        max_length=2,
        choices=[
            ('EU', 'EU'),
            ('US', 'US'),
            ('UK', 'UK')
        ],
        default='EU'
    )
    offer_size_36 = models.BooleanField(verbose_name='36 EU', default=False)
    offer_size_36_5 = models.BooleanField(verbose_name='36.5 EU', default=False)
    offer_size_37 = models.BooleanField(verbose_name='37 EU', default=False)
    offer_size_37_5 = models.BooleanField(verbose_name='37.5 EU', default=False)
    offer_size_38 = models.BooleanField(verbose_name='38 EU', default=False)
    offer_size_38_5 = models.BooleanField(verbose_name='38.5 EU', default=False)
    offer_size_39 = models.BooleanField(verbose_name='39 EU', default=False)
    offer_size_39_5 = models.BooleanField(verbose_name='39.5 EU', default=False)
    offer_size_40 = models.BooleanField(verbose_name='40 EU', default=False)
    offer_size_40_5 = models.BooleanField(verbose_name='40.5 EU', default=False)
    offer_size_41 = models.BooleanField(verbose_name='41 EU', default=False)
    offer_size_41_5 = models.BooleanField(verbose_name='41.5 EU', default=False)
    offer_size_42 = models.BooleanField(verbose_name='42 EU', default=False)
    offer_size_42_5 = models.BooleanField(verbose_name='42.5 EU', default=False)
    offer_size_43 = models.BooleanField(verbose_name='43 EU', default=False)
    offer_size_43_5 = models.BooleanField(verbose_name='43.5 EU', default=False)
    offer_size_44 = models.BooleanField(verbose_name='44 EU', default=False)
    offer_size_44_5 = models.BooleanField(verbose_name='44.5 EU', default=False)
    offer_size_45 = models.BooleanField(verbose_name='45 EU', default=False)
    offer_size_45_5 = models.BooleanField(verbose_name='45.5 EU', default=False)
    offer_size_46 = models.BooleanField(verbose_name='46 EU', default=False)
    offer_size_46_5 = models.BooleanField(verbose_name='46.5 EU', default=False)
    offer_size_47 = models.BooleanField(verbose_name='47 EU', default=False)
    offer_size_47_5 = models.BooleanField(verbose_name='47.5 EU', default=False)
    offer_premium = models.BooleanField(
        verbose_name='Премиум',
        default=False
    )
    offer_new_users = models.BooleanField(
        verbose_name='Новые пользователи',
        default=False
    )

    postpone = models.BooleanField(
        verbose_name='Отложить',
        default=False
    )
    postpone_time = models.DateTimeField(
        verbose_name='Время публикации (часовой пояс UTC)',
        default=datetime(2020, 1, 1)
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.postpone:
                self.status = 'postponed'
            else:
                self.status = 'queue'

        elif self.status == 'postponed' and not self.postpone:
            self.status = 'queue'

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Отложенный пост'
        verbose_name_plural = 'Отложенные посты'

    def __str__(self):
        timedate = self.created.isoformat(sep=' ', timespec='seconds')
        timedate = timedate[:timedate.index('+')]
        return ('Оффер ' if self.type == 'offer' else 'Пост ') + timedate


class Draft(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=100,
        unique=True
    )

    text = models.TextField(
        verbose_name='Текст (форматированный, 200 символов для постов с картинкой сверху)',
        max_length=5000
    )

    class Meta:
        verbose_name = 'Черновик'
        verbose_name_plural = 'Черновики'

    def __str__(self):
        return self.title


class FeedbackDialogue(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=BotUser,
        related_name='dialogue',
        on_delete=models.CASCADE
    )

    data = models.TextField(
        blank=True,
        default=''
    )
    unread = models.BooleanField(
        default=True
    )

    last_message_sender = models.CharField(
        verbose_name='Отправитель последнего сообщения',
        max_length=7,
        choices=[
            ('user', 'Пользователь'),
            ('support', 'Поддержка')
        ],
        default='user'
    )
    last_message_time = models.DateTimeField(
        verbose_name='Время последнего сообщения (часовой пояс UTC)',
        default=datetime.now(timezone.utc)
    )

    status = models.CharField(
        verbose_name='Статус',
        max_length=7,
        choices=[
            ('open', 'Открыт'),
            ('closed', 'Закрыт')
        ],
        default='open'
    )
    marked = models.BooleanField(
        verbose_name='Избранный',
        default=False
    )
    ignored = models.BooleanField(
        verbose_name='Игнор',
        default=False
    )

    draft = models.ForeignKey(
        verbose_name='Черновик',
        to='Draft',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    message = models.TextField(
        verbose_name='Текст (форматированный)',
        max_length=5000,
        blank=True,
        null=True
    )
    button_title = models.CharField(
        verbose_name='Текст кнопки',
        max_length=100,
        blank=True,
        null=True
    )
    button_link = models.URLField(
        verbose_name='Ссылка кнопки',
        blank=True,
        null=True
    )

    def validate_image(image):
        filesize = image.file.size
        limit_mb = 1
        if filesize > limit_mb * 1024 * 1024:
            raise ValidationError(f'Максимальный размер файла - {limit_mb}МБ')

    def get_image_path(instance, filename):
        length = 8
        path = ''
        for index in range(length):
            path += choice(ascii_lowercase)
        return path + '.' + filename.split('.')[-1]
    image = models.ImageField(
        verbose_name='Изображение (до 1МБ)',
        upload_to=get_image_path,
        blank=True,
        null=True,
        validators=[validate_image]
    )

    def save(self, *args, **kwargs):
        adding = self._state.adding

        super().save(*args, **kwargs)

        if adding:
            pass

        else:
            bot = TeleBot(settings.BOT_TOKEN, threaded=False)
            user_id = self.user.user_id

            if self.message:
                if self.button_title and self.button_link:
                    markup = types.InlineKeyboardMarkup()
                    markup.row(types.InlineKeyboardButton(text=self.button_title, url=self.button_link))
                else:
                    markup = None
                try:
                    message = self.message.format(user=self.user.first_name)
                except BaseException:
                    message = self.message
                data_message = message
                message = '<b>SaleFinder Support:</b>\n\n' + message
                if self.image:
                    if len(settings.ALLOWED_HOSTS) > 1:
                        image_link = f'https://{settings.ALLOWED_HOSTS[1]}/media/{self.image}'
                    else:
                        image_link = f'https://{settings.ALLOWED_HOSTS[0]}/media/{self.image}'
                    message = f'<a href="{image_link}">&#8204;</a>' + message
                bot.send_message(user_id,
                    message,
                    parse_mode='html',
                    reply_markup=markup
                )
                self.data += '<div class="dialog-message support-message">\n'
                data_time = datetime.now().isoformat(sep=' ', timespec='seconds')
                self.data += f'<div class="dialog-message-time">{data_time}</div>\n'
                self.data += f'<div class="dialog-message-text">{data_message}</div>\n'
                if self.image:
                    self.data += f'<a class="dialog-image" href="{image_link}"><img src="{image_link}" /></a>\n'
                if self.button_title and self.button_link:
                    self.data += f'<a class="dialog-button" href="{self.button_link}">- {self.button_title} -</a>\n'
                self.data += '</div>\n\n'
                self.last_message_sender = 'support'
                self.last_message_time = datetime.now(timezone.utc)

            elif self.image:
                if len(settings.ALLOWED_HOSTS) > 1:
                    image_link = f'https://{settings.ALLOWED_HOSTS[1]}/media/{self.image}'
                else:
                    image_link = f'https://{settings.ALLOWED_HOSTS[0]}/media/{self.image}'
                bot.send_photo(user_id,
                    photo=image_link,
                    caption='<b>SaleFinder Support</b>',
                    parse_mode='html'
                )
                self.data += '<div class="dialog-message support-message">\n'
                data_time = datetime.now().isoformat(sep=' ', timespec='seconds')
                self.data += f'<div class="dialog-message-time">{data_time}</div>\n'
                self.data += f'<a class="dialog-image" href="{image_link}"><img src="{image_link}" /></a>\n'
                self.data += '</div>\n\n'
                self.last_message_sender = 'support'
                self.last_message_time = datetime.now(timezone.utc)

            self.draft = None
            self.message = None
            self.button_title = None
            self.button_link = None
            self.image = None

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'

    def __str__(self):
        return str(self.user)
