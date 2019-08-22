from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.conf import settings

from preferences.admin import PreferencesAdmin
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.admin import GlobalPreferenceAdmin

from bot import models


class BotUserAdmin(admin.ModelAdmin):
    readonly_fields = [
        'created',
        'user_id', 'username', 'first_name', 'last_name',
        'gender', 'sizes',
        'is_premium', 'is_referral_premium',
        'inviter_id', 'amount_of_referrals',
        # 'deleted'
    ]
    fieldsets = [
        ('Данные аккаунта Telegram', {'fields': [
            'user_id', 'username',
            ('first_name', 'last_name')
        ]}),
        ('', {'fields': [
            'created'
        ]}),
        ('Настройки рассылки', {'fields': [
            'configured', 'gender', 'sizes'
        ]}),
        ('Премиум', {'fields': [
            'is_premium',
            'is_paid_premium', 'is_referral_premium'
        ]}),
        ('Реферальная система', {'fields': [
            'inviter_id',
            'amount_of_referrals'
        ]}),
        ('', {'fields': [
            # 'deleted'
        ]})
    ]
    list_display = ['user_id', 'username', 'first_name', 'last_name', 'created', 'configured', 'gender', 'is_premium', 'amount_of_referrals']#, 'deleted']
    search_fields = [
        'user_id', 'username',
        'first_name', 'last_name',
        'inviter_id'
    ]

    def has_view_permission(self, request, *args, **kwargs):
        user = request.user

        if user.username == 'god':
            return True

        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.support_rights:
            return True
        else:
            return False

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_change_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.support_rights:
            return True
        else:
            return False

    def has_delete_permission(self, request, *args, **kwargs):
        return False

    class Media:
        css = {
             'all': ('admin/css/custom_botuser.css',)
        }


def statistics_admin_generate_sizes(gender, min_size, max_size):
    sizes = []

    current_size = min_size
    while current_size < max_size:
        current_sizes = [str(current_size), str(current_size) + '_05']
        if current_size + 1 <= max_size:
            current_sizes += [str(current_size + 1), str(current_size + 1) + '_05']
        current_sizes = [f'total_{gender}_size_{size}' for size in current_sizes]

        sizes.append(tuple(current_sizes))

        current_size += 2

    return sizes


def statistics_admin_generate_men_sizes():
    return statistics_admin_generate_sizes('men', settings.MIN_MAN_SIZE, settings.MAX_MAN_SIZE)


def statistics_admin_generate_women_sizes():
    return statistics_admin_generate_sizes('women', settings.MIN_WOMAN_SIZE, settings.MAX_WOMAN_SIZE)


class StatisticsAdmin(PreferencesAdmin):
    readonly_fields = [
        'total_users', 'total_configured_users',
        'total_men', 'total_women',
        'total_referrals',
        'total_referrals_amount_1', 'total_referrals_amount_2', 'total_referrals_amount_3'
    ]
    fieldsets = [
        ('', {'fields': [
            'total_users', 'total_configured_users'
        ]}),
        ('Мужчины', {'fields': [
            'total_men'
        ] + statistics_admin_generate_men_sizes()}),
        ('Женщины', {'fields': [
            'total_women'
        ] + statistics_admin_generate_women_sizes()}),
        ('Реферальная программа', {'fields': [
            'total_referrals',
            ('total_referrals_amount_1', 'total_referrals_amount_2', 'total_referrals_amount_3')
        ]}),
        ('Нажатия на кнопки за 24 часа', {'fields': [
            ('day_clicks_referral_program', 'day_clicks_rating', 'day_clicks_invite'),
            ('day_clicks_premium', 'day_clicks_setup_spam', 'day_clicks_callback')
        ]}),
        ('Нажатия на кнопки за месяц', {'fields': [
            ('month_clicks_referral_program', 'month_clicks_rating', 'month_clicks_invite'),
            ('month_clicks_premium', 'month_clicks_setup_spam', 'month_clicks_callback')
        ]}),
        ('Нажатия на кнопки за все время', {'fields': [
            ('all_clicks_referral_program', 'all_clicks_rating', 'all_clicks_invite'),
            ('all_clicks_premium', 'all_clicks_setup_spam', 'all_clicks_callback')
        ]})
    ]

    def __getattribute__(self, attr):
        if attr.startswith('total_men_size_') or attr.startswith('total_women_size_'):
            splitted_attr = attr.split('_')
            if splitted_attr[-1] == '05':
                size = int(splitted_attr[-2]) + 0.5
            else:
                size = int(splitted_attr[-1])
            def wrapper(*args, **kwargs):
                return models.Statistics.count_size(splitted_attr[1], float(size))
            wrapper.short_description = f'{size} размер'
            return wrapper
        else:
            return super().__getattribute__(attr)

    def has_view_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        else:
            return False

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_change_permission(self, request, *args, **kwargs):
        return False

    def has_delete_permission(self, request, *args, **kwargs):
        return False

    class Media:
        css = {
             'all': ('admin/css/custom_statistics.css',)
        }


class CustomGlobalPreferenceAdmin(GlobalPreferenceAdmin):
    list_display = ['verbose_name', 'raw_value', 'default_value']
    list_filter = []
    search_fields = []

    ordering = ('id',)

    def has_view_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        else:
            return False

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_change_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        else:
            return False

    def has_delete_permission(self, request, *args, **kwargs):
        return False

    class Media:
        js = ('admin/js/custom_global_preference.js',)


class StaffAdmin(admin.ModelAdmin):
    list_display = ['login', 'content_management_rights', 'support_rights']
    list_editable = ['content_management_rights', 'support_rights']

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        else:
            return ['login', 'password']

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [
                ('Регистрационные данные', {'fields': [
                    'login', 'password'
                ]}),
                ('Права', {'fields': [
                    'content_management_rights', 'support_rights'
                ]})
            ]
        else:
            return [
                ('Регистрационные данные', {'fields': [
                    'login'
                ]}),
                ('Права', {'fields': [
                    'content_management_rights', 'support_rights'
                ]})
            ]

    def has_view_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        else:
            return False

    def has_add_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        else:
            return False

    def has_change_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        else:
            return False

    def has_delete_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        else:
            return False

    class Media:
        css = {
            'all': ('admin/css/custom_staff.css',)
        }


class PostponedPostAdmin(admin.ModelAdmin):
    list_display = ['type', 'created', 'status', 'html_text', 'html_buttons', 'image', 'image_place_custom']
    list_display_links = ['type', 'created']
    search_fields = ['text']
    list_per_page = 10

    def html_text(self, obj):
        try:
            text = obj.text.format(shoe_sizes="(размеры)")
            return format_html(f'<span style="white-space: pre-wrap;">{text}</span>')
        except:
            return format_html('<b>Ошибка предросмотра!</b></br>Проверьте формат записи тегов')
    html_text.short_description = 'Текст'

    def html_buttons(self, obj):
        try:
            buttons = ''
            for index in range(1, obj.amount_of_buttons + 1):
                title = getattr(obj, f'button_{index}_title')
                link = getattr(obj, f'button_{index}_link')
                if title and link:
                    buttons += f'<a href="{link}">- {title} -</a></br>'
            return format_html(buttons)
        except:
            return format_html('<b>Ошибка вывода кнопок!</b></br>Проверьте формат записи кнопок')
    html_buttons.short_description = 'Кнопки'

    def image_place_custom(self, obj):
        if obj.image:
            return 'Снизу' if obj.image_place == 'bottom' else 'Сверху'
        else:
            return None
    image_place_custom.short_description = 'Расположение изображения'

    def postpone_time_proxy(self, obj):
        return obj.postpone_time
    postpone_time_proxy.short_description = 'Время публикации (часовой пояс UTC)'

    def hidden_drafts(self):
        return '__secret_delimiter__'.join(
            f'{draft.pk}__secret_inner_delimiter__{draft.text}'
                for draft in models.Draft.objects.all()
        )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [
                ('Общая информация', {'description': self.hidden_drafts(), 'fields': [
                    'type'
                ]}),
                ('Внешний вид', {'fields': [
                    'draft', 'text',
                    'amount_of_buttons',
                    ('button_1_title', 'button_1_link'),
                    ('button_2_title', 'button_2_link'),
                    ('button_3_title', 'button_3_link'),
                    ('button_4_title', 'button_4_link'),
                    'image'#, 'image_place'
                ]}),
                ('Сегментация рассылки', {'fields': [
                    'post_all', 'post_need_spam_setup',
                    'post_0_referrals', 'post_1_referrals', 'post_2_referrals', 'post_3_and_more_referrals'
                ]}),
                ('Настройки оффера', {'fields': [
                    'offer_gender',
                    'offer_sizes_type',
                    ('offer_size_36', 'offer_size_36_5', 'offer_size_37', 'offer_size_37_5'),
                    ('offer_size_38', 'offer_size_38_5', 'offer_size_39', 'offer_size_39_5'),
                    ('offer_size_40', 'offer_size_40_5', 'offer_size_41', 'offer_size_41_5'),
                    ('offer_size_42', 'offer_size_42_5', 'offer_size_43', 'offer_size_43_5'),
                    ('offer_size_44', 'offer_size_44_5', 'offer_size_45', 'offer_size_45_5'),
                    ('offer_size_46', 'offer_size_46_5', 'offer_size_47', 'offer_size_47_5'),
                    'offer_premium', 'offer_new_users'
                ]}),
                ('Откладывание поста', {'fields': [
                    'postpone', 'postpone_time'
                ]})
            ]

        else:
            return [
                ('Общая информация', {'description': self.hidden_drafts(), 'fields': [
                    'type', 'created',
                    'status'
                ] if obj.status != 'done' else [
                    'type', 'created',
                    'status', #'amount_of_receivers'
                ]}),
                ('Внешний вид', {'fields': (['draft'] if obj.type == 'offer' else []) + [
                    'text',
                    'amount_of_buttons',
                    ('button_1_title', 'button_1_link'),
                    ('button_2_title', 'button_2_link'),
                    ('button_3_title', 'button_3_link'),
                    ('button_4_title', 'button_4_link'),
                    'image'#, 'image_place'
                ]})
            ] + (
                [('Сегментация рассылки', {'fields': [
                    'post_all', 'post_need_spam_setup',
                    'post_0_referrals', 'post_1_referrals', 'post_2_referrals', 'post_3_and_more_referrals'
                ]})] if obj.type == 'post' else [('Настройки оффера', {'fields': [
                    'offer_gender',
                    'offer_sizes_type',
                    ('offer_size_36', 'offer_size_36_5', 'offer_size_37', 'offer_size_37_5'),
                    ('offer_size_38', 'offer_size_38_5', 'offer_size_39', 'offer_size_39_5'),
                    ('offer_size_40', 'offer_size_40_5', 'offer_size_41', 'offer_size_41_5'),
                    ('offer_size_42', 'offer_size_42_5', 'offer_size_43', 'offer_size_43_5'),
                    ('offer_size_44', 'offer_size_44_5', 'offer_size_45', 'offer_size_45_5'),
                    ('offer_size_46', 'offer_size_46_5', 'offer_size_47', 'offer_size_47_5'),
                    'offer_premium', 'offer_new_users'
                ]})]
            ) + [
                ('Откладывание поста', {'fields': [
                    'postpone', 'postpone_time' if (self.has_change_permission(request, obj) or not obj.postpone) else 'postpone_time_proxy'
                ]})
            ]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        else:
            return ['type', 'created', 'postpone_custom', 'status']

    def has_view_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.content_management_rights:
            return True
        else:
            return False

    def has_add_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.content_management_rights:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return (obj is None) or (obj.status in ['postponed'])
        elif user.is_superuser and user.staff_data.content_management_rights:
            return (obj is None) or (obj.status in ['postponed'])
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return (obj is None) or (obj.status in ['postponed', 'queue', 'done'])
        elif user.is_superuser and user.staff_data.content_management_rights:
            return (obj is None) or (obj.status in ['postponed', 'queue', 'done'])
        else:
            return False

    class Media:
        css = {
            'all': ('admin/css/custom_postponedpost.css',)
        }
        js = ('admin/js/custom_postponedpost.js',)


class DraftAdmin(admin.ModelAdmin):
    list_display = ['edit', 'title', 'text', 'html_text']
    list_display_links = ['edit']
    list_editable = ['title', 'text']

    ordering = ('title',)

    def html_text(self, obj):
        try:
            text = obj.text.format(shoe_sizes="(размеры)")
            return format_html(f'<span style="white-space: pre-wrap;">{text}</span>')
        except:
            return format_html('<b>Ошибка предросмотра!</b></br>Проверьте формат записи тегов')
    html_text.short_description = 'Предпросмотр текста'

    def edit(self, obj):
        return 'Изменить'
    edit.short_description = ''

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [('Новый черновик', {'fields': [
                'title', 'text'
            ]})]

        else:
            return [('Черновик', {'fields': [
                'title', 'text'
            ]})]

    def has_view_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.content_management_rights:
            return True
        else:
            return False

    def has_add_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.content_management_rights:
            return True
        else:
            return False

    def has_change_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.content_management_rights:
            return True
        else:
            return False

    def has_delete_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.content_management_rights:
            return True
        else:
            return False

    class Media:
        css = {
            'all': ('admin/css/custom_draft.css',)
        }
        js = ('admin/js/custom_draft.js',)


class FeedbackDialogueIgnoredFilter(admin.SimpleListFilter):
    title = 'Игнор'
    parameter_name = 'ignored'

    def lookups(self, request, model_admin):
        return (
            ('all', 'Все'),
            ('ignored', 'Да'),
        )

    def queryset(self, request, queryset):
        ignored = request.GET.get('ignored')

        if ignored == 'all':
            return queryset.all()
        elif ignored == 'ignored':
            return queryset.filter(ignored=True)
        else:
            return queryset.filter(ignored=False)

    def choices(self, cl):
        yield {
            'selected': self.value() is None,
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': 'Нет',
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class FeedbackDialogueAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_first_name', 'user_last_name', 'last_message_sender', 'custom_unread', 'last_message_time', 'status', 'marked', 'ignored']
    list_editable = ['status', 'marked', 'ignored']
    search_fields = ['user__user_id', 'user__username', 'user__first_name', 'user__last_name']
    list_filter = ['status', 'marked', FeedbackDialogueIgnoredFilter]
    list_per_page = 15

    ordering = ('-last_message_time',)

    def hidden_drafts(self):
        return '__secret_delimiter__'.join(
            f'{draft.pk}__secret_inner_delimiter__{draft.text}'
                for draft in models.Draft.objects.all()
        )

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            obj.unread = False
            obj.save()
        fieldsets = [
            ('Пользователь', {'fields': [
                'user_link'
            ]}),
            ('Диалог', {'fields': [
                'data'
            ]}),
            ('Состояния', {'fields': [
                'status', 'marked', 'ignored'
            ]}),
            ('Новое сообщение', {'description': self.hidden_drafts(), 'fields': [
                'draft', 'message',
                ('button_title', 'button_link'),
                'image'#, 'image_place'
            ]}),
        ]
        return fieldsets
    readonly_fields = [
        'user_link'
    ]

    def user_link(self, obj):
        return format_html(
            f'<a href="/admin/bot/botuser/{obj.user.pk}/change/">{str(obj.user)}</a>'
        )
    user_link.short_description = 'Пользователь'

    def custom_unread(self, obj):
        return None if obj.last_message_sender == 'support' else not obj.unread
    custom_unread.short_description = 'Прочитано'
    custom_unread.boolean = True

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'Имя'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Фамилия'

    def has_view_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.support_rights:
            return True
        else:
            return False

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_change_permission(self, request, *args, **kwargs):
        user = request.user
        if user.username == 'god':
            return True
        if user.is_superuser and user.username == settings.ADMIN:
            return True
        elif user.is_superuser and user.staff_data.support_rights:
            return True
        else:
            return False

    def has_delete_permission(self, request, *args, **kwargs):
        return False

    class Media:
        css = {
            'all': ('admin/css/custom_feedbackdialogue.css',)
        }
        js = ('admin/js/custom_feedbackdialogue.js',)


admin.site.site_header = 'Администрирование бота'
admin.site.site_title = 'Администрирование SaleFinder'
admin.site.site_url = ''

admin.site.register(models.BotUser, BotUserAdmin)
admin.site.register(models.Statistics, StatisticsAdmin)
admin.site.register(models.Staff, StaffAdmin)

admin.site.register(models.PostponedPost, PostponedPostAdmin)
admin.site.register(models.Draft, DraftAdmin)

admin.site.unregister(GlobalPreferenceModel)
admin.site.register(GlobalPreferenceModel, CustomGlobalPreferenceAdmin)

admin.site.register(models.FeedbackDialogue, FeedbackDialogueAdmin)

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)
