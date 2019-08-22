from dynamic_preferences.types import IntegerPreference, StringPreference, LongStringPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

texts = Section('texts')


@global_preferences_registry.register
class PremiumPrice(IntegerPreference):
    name = 'premium_price'
    verbose_name = 'Цена премиум подписки, RUB'
    default = 500


@global_preferences_registry.register
class FirstGreetingText(LongStringPreference):
    section = texts
    name = 'first_greeting'
    verbose_name = 'Приветственное сообщение #1'
    default = 'Привет! Меня зовут SaleFinder.\n\nЯ помогаю людям экономить на покупке их любимых кроссовок.'


@global_preferences_registry.register
class SecondGreetingText(LongStringPreference):
    section = texts
    name = 'second_greeting'
    verbose_name = 'Приветственное сообщение #2'
    default = 'Смотри, какие предложения я уже приготовил для тебя👇'


@global_preferences_registry.register
class ThirdGreetingText(LongStringPreference):
    section = texts
    name = 'third_greeting'
    verbose_name = 'Приветственное сообщение #3'
    default = 'Но они могут тебе не подойти, так как я еще не знаю твоего пола и размера обуви.\nЖми на кнопку <b>Настройка рассылки</b> и следуй дальнейшим инструкциям.'


@global_preferences_registry.register
class SpamSetupGenderButtonText(LongStringPreference):
    section = texts
    name = 'spam_setup_gender_button'
    verbose_name = 'Выбор пола'
    default = 'Выберите пол'


@global_preferences_registry.register
class SpamSetupSizeButtonText(LongStringPreference):
    section = texts
    name = 'spam_setup_size_button'
    verbose_name = 'Выбор размеров'
    default = 'Выберите размеры обуви EU'


@global_preferences_registry.register
class SpamSetupSuccessButtonText(LongStringPreference):
    section = texts
    name = 'spam_setup_success_button'
    verbose_name = 'Успешная настройка рассылки'
    default = 'Рассылка настроена успешно'


@global_preferences_registry.register
class ReferralProgramButtonText(LongStringPreference):
    section = texts
    name = 'referral_program_button'
    verbose_name = 'Реферальная программа'
    default = 'Приглашено друзей: {number}\n\nПриглашай друзей и получай доступ к разделу <b>Премиум скидки</b>, а также возможность участия в розыгрышах кроссовок.'


@global_preferences_registry.register
class ReferralProgramInviteText(LongStringPreference):
    section = texts
    name = 'referral_program_invite'
    verbose_name = 'Пригласительное сообщение'
    default = 'SaleFinder - бот, высылающий самые большие скидки на кроссовки нужного размера в крупнейших интернет магазинах.\nПопробуй 😏'


@global_preferences_registry.register
class ReferralProgramInviteButtonText(StringPreference):
    section = texts
    name = 'referral_program_invite_button'
    verbose_name = 'Кнопка пригласительного сообщения'
    default = '😏 Попробовать'


@global_preferences_registry.register
class CallbackButtonText(LongStringPreference):
    section = texts
    name = 'callback_button'
    verbose_name = 'Обратная связь'
    default = 'Пришлите ваш вопрос или предложение по работе и улучшению в бота @...'


@global_preferences_registry.register
class CallbackBlockedText(LongStringPreference):
    section = texts
    name = 'callback_blocked'
    verbose_name = 'Заблокированное сообщение обратной связи'
    default = 'Для связи с поддержкой нажмите <b>Обратная связь</b>.'


@global_preferences_registry.register
class CallbackAcceptedText(LongStringPreference):
    section = texts
    name = 'callback_accepted'
    verbose_name = 'Принятое сообщение обратной связи'
    default = 'Ваше сообщение принято!'


@global_preferences_registry.register
class PremiumTrueButtonText(LongStringPreference):
    section = texts
    name = 'premium_true_button'
    verbose_name = 'Действующий премиум аккаунт'
    default = 'Вам открыт доступ к разделу премиум скидки.\nНовые товары будут высылаться в обычном режиме.'


@global_preferences_registry.register
class PremiumFalseButtonText(LongStringPreference):
    section = texts
    name = 'premium_false_button'
    verbose_name = 'Информация о премиуме'
    default = 'Премиум скидки - это возможность получать предложения с самыми большие скидками и эксклюзивными кроссовками.\n\n<b>Как получить доступ?</b>\nЕсть два варианта:\n    Платно: Стоимость - 500 рублей\n    Бесплатно: Для этого нужно пригласить в бота от трех друзей по своей реферальной ссылке. Сделать это можно в разделе <b>Реферальная программа</b>'
