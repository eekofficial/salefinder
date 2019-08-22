from random import randint
from datetime import datetime, timezone, timedelta
from time import time
from collections import Counter
from requests import get
from string import ascii_lowercase
from random import choice
import os
import html
import hashlib

import telebot

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from dynamic_preferences.registries import global_preferences_registry

from bot import models

SHOW_ERRORS = False

MIN_MAN_SIZE, MAX_MAN_SIZE = settings.MIN_MAN_SIZE, settings.MAX_MAN_SIZE
MIN_WOMAN_SIZE, MAX_WOMAN_SIZE = settings.MIN_WOMAN_SIZE, settings.MAX_WOMAN_SIZE

global_preferences = global_preferences_registry.manager()

bot = telebot.TeleBot(settings.BOT_TOKEN, threaded=True)
bot_username = bot.get_me().username


main_reply_keyboard = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True
)
main_reply_keyboard.row(
    telebot.types.KeyboardButton('Настройка рассылки'),
    telebot.types.KeyboardButton('Реферальная программа')
)
main_reply_keyboard.row(
    telebot.types.KeyboardButton('Обратная связь'),
    telebot.types.KeyboardButton('Премиум скидки')
)


gender_reply_keyboard = telebot.types.InlineKeyboardMarkup()
gender_reply_keyboard.row(
    telebot.types.InlineKeyboardButton(
        text='Мужской',
        callback_data='spam_setup_gender_male'
    )
)
gender_reply_keyboard.row(
    telebot.types.InlineKeyboardButton(
        text='Женский',
        callback_data='spam_setup_gender_female'
    )
)
gender_reply_keyboard.row(
    telebot.types.InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data='spam_setup_gender_back'
    )
)


referral_rating_reply_keyboard = telebot.types.InlineKeyboardMarkup()
referral_rating_reply_keyboard.row(
    telebot.types.InlineKeyboardButton(
        text='За неделю',
        callback_data='referral_program_rating_week'
    )
)
referral_rating_reply_keyboard.row(
    telebot.types.InlineKeyboardButton(
        text='За месяц',
        callback_data='referral_program_rating_month'
    )
)
referral_rating_reply_keyboard.row(
    telebot.types.InlineKeyboardButton(
        text='За все время',
        callback_data='referral_program_rating_all'
    )
)
referral_rating_reply_keyboard.row(
    telebot.types.InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data='referral_program_back'
    )
)


def message_error_handler(function):
    def wrapper(message):
        try:
            return function(message)

        except BaseException as error:
            if SHOW_ERRORS:
                chat_id = message.chat.id
                bot.send_message(chat_id,
                    f'{type(error).__name__}:\n{error}'
                )

    return wrapper


def click_handler(button):
    def decorator(function):
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)

            try:
                click = models.Click(button=button)
                click.save()
            except BaseException:
                pass

            return result

        return wrapper

    return decorator


FLOOD_AMOUNT = 5
FLOOD_TIME = 7
FLOOD_MESSAGE_TIME = 3


def flood_handler(function):
    def wrapper(message):
        last_messages_time = []

        message_time = time()
        try:
            db_user = models.BotUser.objects.get(user_id=message.from_user.id)
            last_messages_time = [float(record) for record in (db_user.last_messages_time or '').split()]
            last_messages_time.append(message_time)
            last_messages_time = last_messages_time[-FLOOD_AMOUNT:]
            last_messages_time_str = ' '.join([str(record) for record in last_messages_time])
            db_user.last_messages_time = last_messages_time_str
            db_user.save()
        except BaseException:
            pass

        if len(last_messages_time) == FLOOD_AMOUNT:
            delta = last_messages_time[-1] - last_messages_time[0]

            if delta < FLOOD_TIME:
                db_user = models.BotUser.objects.get(user_id=message.from_user.id)
                if time() - (db_user.last_flood_message_time or 0) > FLOOD_MESSAGE_TIME:
                    db_user.last_flood_message_time = time()
                    db_user.save()
                    bot.send_message(message.from_user.id,
                        'Сработала защита от множественных нажатий!'
                    )

            else:
                return function(message)

        else:
            return function(message)

    return wrapper


@bot.message_handler(commands=['start'])
@flood_handler
@message_error_handler
def handle_newcomer(message):
    chat_id = message.chat.id
    user = message.from_user

    splitted_message = message.text.split()
    if len(splitted_message) > 1:
        inviter_id = int(splitted_message[1])
    else:
        inviter_id = None

    try:
        db_user = models.BotUser(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )
        if inviter_id is not None:
            db_user.inviter_id = inviter_id
        db_user.save()

    except BaseException:
        pass

    bot.send_message(chat_id,
        global_preferences['texts__first_greeting'],
        parse_mode='html'
    )

    male_offer = models.PostponedPost.objects.filter(
        type='offer', status='done', offer_gender='male',
        offer_premium=False, offer_new_users=True
    ).order_by('-created').first()
    female_offer = models.PostponedPost.objects.filter(
        type='offer', status='done', offer_gender='female',
        offer_premium=False, offer_new_users=True
    ).order_by('-created').first()

    bot.send_message(chat_id,
        global_preferences['texts__second_greeting'],
        parse_mode='html'
    )
    if not male_offer and not female_offer:
        bot.send_message(chat_id,
            'Предложения отсутствуют!'
        )

    if male_offer:
        send_postponed_post(chat_id, None, male_offer)
    if female_offer:
        send_postponed_post(chat_id, None, female_offer)

    bot.send_message(chat_id,
        global_preferences['texts__third_greeting'],
        parse_mode='html',
        reply_markup=main_reply_keyboard
	)


@bot.message_handler(regexp='^Настройка рассылки$')
@click_handler('setup_spam')
@flood_handler
@message_error_handler
def handle_spam_setup_button(message):
    chat_id = message.chat.id
    user = message.from_user

    db_user = models.BotUser.objects.get(user_id=user.id)
    try:
        if db_user.last_setup_spam_message_id:
            bot.delete_message(chat_id,
                db_user.last_setup_spam_message_id
            )
    except BaseException:
        pass

    sent_message = bot.send_message(chat_id,
        global_preferences['texts__spam_setup_gender_button'],
        parse_mode='html',
        reply_markup=gender_reply_keyboard
    )
    db_user = models.BotUser.objects.get(user_id=user.id)
    db_user.last_setup_spam_message_id = sent_message.message_id
    db_user.save()


def create_sizes_reply_keyboard(gender, sizes=None):
    if sizes is None:
        sizes = []
    (min_size, max_size) = (MIN_MAN_SIZE, MAX_MAN_SIZE) if gender == 'male' else (MIN_WOMAN_SIZE, MAX_WOMAN_SIZE)

    sizes_reply_keyboard = telebot.types.InlineKeyboardMarkup()

    for size in range(min_size, max_size):
        left_size = size
        right_size = size + 0.5

        sizes_reply_keyboard.row(
            telebot.types.InlineKeyboardButton(
                text=str(left_size) + (' *' if float(left_size) in sizes else ''),
                callback_data=f'spam_setup_size_{left_size}'
            ),
            telebot.types.InlineKeyboardButton(
                text=str(right_size) + (' *' if float(right_size) in sizes else ''),
                callback_data=f'spam_setup_size_{right_size}'
            )
        )

    sizes_reply_keyboard.row(
        telebot.types.InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='spam_setup_sizes_back'
        ),
        telebot.types.InlineKeyboardButton(
            text='➡ Далее️️',
            callback_data='spam_setup_done'
        )
    )

    return sizes_reply_keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('spam_setup'))
def handle_spam_setup_callback(call):
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user = call.from_user

        data = call.data

        if data == 'spam_setup_gender_back':
            bot.delete_message(
                chat_id,
                message_id
            )

        elif data in ['spam_setup_gender_male', 'spam_setup_gender_female']:
            if data == 'spam_setup_gender_male':
                gender = 'male'
            elif data == 'spam_setup_gender_female':
                gender = 'female'
            db_user = models.BotUser.objects.get(user_id=user.id)
            db_user.gender = gender
            db_user.setup_spam_checked_sizes = ''
            db_user.save()

            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                text=global_preferences['texts__spam_setup_size_button'],
                parse_mode='html',
                reply_markup=create_sizes_reply_keyboard(gender)
            )

        elif data.startswith('spam_setup_size_'):
            size = float(data.split('_')[-1])
            db_user = models.BotUser.objects.get(user_id=user.id)
            db_user_sizes = [float(size) for size in db_user.setup_spam_checked_sizes.split()]
            if size not in db_user_sizes:
                db_user_sizes.append(size)
            else:
                db_user_sizes.remove(size)
            db_user.setup_spam_checked_sizes = ' '.join([str(size) for size in sorted(db_user_sizes)])
            db_user.save()

            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                reply_markup=create_sizes_reply_keyboard(db_user.gender, db_user_sizes)
            )

        elif data == 'spam_setup_sizes_back':
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                text=global_preferences['texts__spam_setup_gender_button'],
                parse_mode='html',
                reply_markup=gender_reply_keyboard
            )

        elif data == 'spam_setup_done':
            db_user = models.BotUser.objects.get(user_id=user.id)
            if not db_user.setup_spam_checked_sizes:
                bot.send_message(chat_id,
                    'Нужно выбрать как минимум 1 размер!'
                )

            else:
                if not db_user.configured and db_user.inviter_id:
                    try:
                        inviter = models.BotUser.objects.get(user_id=db_user.inviter_id)
                        inviter.amount_of_referrals += 1
                        inviter.save()
                    except BaseException:
                        pass
                db_user.configured = True
                db_user.sizes = db_user.setup_spam_checked_sizes
                db_user.save()

                bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                    text=global_preferences['texts__spam_setup_success_button'],
                    parse_mode='html'
                )

    except BaseException as error:
        if SHOW_ERRORS:
            bot.send_message(call.message.chat.id,
                f'{type(error).__name__}:\n{error}'
            )

    finally:
        bot.answer_callback_query(call.id)


def create_referral_reply_keyboard(user_id):
    referral_reply_keyboard = telebot.types.InlineKeyboardMarkup()
    referral_reply_keyboard.row(
        telebot.types.InlineKeyboardButton(
            text='Рейтинг',
            callback_data='referral_program_rating'
        )
    )
    referral_reply_keyboard.row(
        telebot.types.InlineKeyboardButton(
            text='Пригласить друга',
            switch_inline_query=user_id
        )
    )
    referral_reply_keyboard.row(
        telebot.types.InlineKeyboardButton(
            text='Получить реф-ссылку',
            callback_data='referral_program_get_link'
        )
    )
    referral_reply_keyboard.row(
        telebot.types.InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='referral_program_close'
        )
    )

    return referral_reply_keyboard


@bot.message_handler(regexp='^Реферальная программа$')
@click_handler('referral_program')
@flood_handler
@message_error_handler
def handle_referral_program_button(message):
    chat_id = message.chat.id
    user = message.from_user

    db_user = models.BotUser.objects.get(user_id=user.id)

    number_of_referrals = db_user.amount_of_referrals

    try:
        if db_user.last_referral_program_message_id:
            bot.delete_message(chat_id,
                db_user.last_referral_program_message_id
            )
    except BaseException:
        pass

    sent_message = bot.send_message(chat_id,
        global_preferences['texts__referral_program_button'].format(
            number=number_of_referrals
        ),
        parse_mode='html',
        reply_markup=create_referral_reply_keyboard(user.id)
    )
    db_user = models.BotUser.objects.get(user_id=user.id)
    db_user.last_referral_program_message_id = sent_message.message_id
    db_user.save()


@bot.callback_query_handler(func=lambda call: call.data.startswith('referral_program'))
def handle_referral_program_callback(call):
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user = call.from_user

        data = call.data

        if data == 'referral_program_close':
            bot.delete_message(
                chat_id,
                message_id
            )

        elif data == 'referral_program_get_link':
            link = f'https://t.me/{bot_username}?start={user.id}'
            bot.send_message(chat_id,
                link
            )

        elif data == 'referral_program_rating':
            click = models.Click(button='rating')
            click.save()

            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                reply_markup=referral_rating_reply_keyboard
            )

        elif data.startswith('referral_program_rating_'):
            period = data.split('_')[-1]

            text = 'Рейтинг за '
            if period == 'week':
                text += 'неделю:\n\n'
            elif period == 'month':
                text += 'месяц:\n\n'
            else:
                text += 'все время:\n\n'

            now = datetime.now(timezone.utc)

            if period == 'week':
                from_time = now - timedelta(7)
            elif period == 'month':
                from_time = now - timedelta(30)
            else:
                from_time = now - timedelta(365 * 10)

            new_users = models.BotUser.objects.filter(created__gte=from_time, configured=True, inviter_id__isnull=False)
            inviter_ids = [user.inviter_id for user in new_users]
            amounts = Counter(inviter_ids)
            top_users_ids = [element[0] for element in amounts.most_common(10)]
            top_users = list(models.BotUser.objects.filter(user_id__in=top_users_ids))
            top_users_debug = sorted([(amounts[user.user_id], user.first_name, user.last_name or '')
                for user in top_users
            ], reverse=True)

            if not top_users:
                text += 'Нет данных за выбранный период!'
            else:
                for index, user in enumerate(top_users_debug, 1):
                    text += f'{index}. {user[1]}{" " + user[2] if user[2] else ""}: {user[0]}\n'

            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                text=text,
                reply_markup=referral_rating_reply_keyboard
            )

        elif data == 'referral_program_back':
            db_user = models.BotUser.objects.get(user_id=user.id)
            number_of_referrals = db_user.amount_of_referrals

            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                text=global_preferences['texts__referral_program_button'].format(
                    number=number_of_referrals
                ),
                parse_mode='html',
                reply_markup=create_referral_reply_keyboard(user.id)
            )

    except BaseException as error:
        if SHOW_ERRORS:
            bot.send_message(chat_id,
                f'{type(error).__name__}:\n{error}'
            )

    finally:
        bot.answer_callback_query(call.id)


@bot.inline_handler(func=lambda query: True)
@click_handler('invite')
def handle_referral_inline_invite(query):
    invite_reply_keyboard = telebot.types.InlineKeyboardMarkup()
    invite_reply_keyboard.row(
        telebot.types.InlineKeyboardButton(
            text=global_preferences['texts__referral_program_invite_button'],
            url=f'https://t.me/{bot_username}?start={query.query}'
        )
    )

    bot.answer_inline_query(
        inline_query_id=query.id,

        is_personal=True,
        cache_time=0,
        next_offset='',

        results=[
            telebot.types.InlineQueryResultArticle(id=randint(0, 2 ** 32 - 1),
                title='Поделиться ссылкой',
                input_message_content=telebot.types.InputTextMessageContent(
                    message_text=global_preferences['texts__referral_program_invite'],
                    parse_mode='html'
                ),
                reply_markup=invite_reply_keyboard
            )
        ]
    )


@bot.message_handler(regexp='^Обратная связь$')
@click_handler('callback')
@flood_handler
@message_error_handler
def handle_callback_button(message):
    chat_id = message.chat.id
    user = message.from_user
    db_user = models.BotUser.objects.get(user_id=user.id)

    bot.send_message(chat_id,
        global_preferences['texts__callback_button'],
        parse_mode='html',
        reply_markup=main_reply_keyboard
    )

    db_user.feedback_enabled = True
    db_user.save()


MERCHANT_ID = '100054'
SECRET = 'xrec33me'


@bot.message_handler(regexp='^Премиум скидки$')
@click_handler('premium')
@flood_handler
@message_error_handler
def handle_premium_discounts_button(message):
    chat_id = message.chat.id
    user = message.from_user
    db_user = models.BotUser.objects.get(user_id=user.id)

    if db_user.is_premium():
        sent_message_id = bot.send_message(chat_id,
            global_preferences['texts__premium_true_button'],
            parse_mode='html',
            reply_markup=main_reply_keyboard
        ).message_id

    else:
        amount = int(global_preferences['premium_price'])
        sign = hashlib.md5((f'{MERCHANT_ID}:{amount}:{SECRET}:{user.id}').encode()).hexdigest()
        url = f'https://www.free-kassa.ru/merchant/cash.php?m={MERCHANT_ID}&oa={amount}&o={user.id}&s={sign}&lang=ru'
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Купить подписку', url=url))
        sent_message_id = bot.send_message(chat_id,
            global_preferences['texts__premium_false_button'],
            parse_mode='html',
            reply_markup=main_reply_keyboard
        ).message_id

        sent_message_id = bot.send_message(chat_id, 'Метод оплаты - Free-Kassa', reply_markup=keyboard).message_id

    db_user = models.BotUser.objects.get(user_id=user.id)
    try:
        if db_user.last_premium_discounts_message_id:
            bot.delete_message(chat_id,
                db_user.last_premium_discounts_message_id
            )
    except BaseException as error:
        pass

    db_user = models.BotUser.objects.get(user_id=user.id)
    db_user.last_premium_discounts_message_id = sent_message_id
    db_user.save()


@require_POST
@csrf_exempt
def handle_free_kassa_notification(request):
    user_id = int(request.POST['MERCHANT_ORDER_ID'])
    chat_id = user_id

    db_user = models.BotUser.objects.get(user_id=user_id)
    db_user.is_paid_premium = True
    db_user.save()

    try:
        if db_user.last_premium_discounts_message_id:
            bot.delete_message(chat_id,
                db_user.last_premium_discounts_message_id
            )
    except BaseException as error:
        pass

    sent_message_id = bot.send_message(chat_id,
        global_preferences['texts__premium_true_button'],
        parse_mode='html',
        reply_markup=main_reply_keyboard
    ).message_id

    db_user = models.BotUser.objects.get(user_id=user_id)
    db_user.last_premium_discounts_message_id = sent_message_id
    db_user.save()

    return HttpResponse('YES', content_type="text/plain")


@bot.pre_checkout_query_handler(func=lambda call: True)
def handle_premium_pre_checkout(call):
    bot.answer_pre_checkout_query(call.id, True)


@bot.message_handler(content_types=['successful_payment'])
@message_error_handler
def handle_premium_payment(message):
    chat_id = message.chat.id
    user = message.from_user
    db_user = models.BotUser.objects.get(user_id=user.id)

    db_user.is_paid_premium = True
    db_user.save()

    try:
        if db_user.last_premium_discounts_message_id:
            bot.delete_message(chat_id,
                db_user.last_premium_discounts_message_id
            )
    except BaseException as error:
        pass

    sent_message_id = bot.send_message(chat_id,
        global_preferences['texts__premium_true_button'],
        parse_mode='html',
        reply_markup=main_reply_keyboard
    ).message_id

    db_user = models.BotUser.objects.get(user_id=user.id)
    db_user.last_premium_discounts_message_id = sent_message_id
    db_user.last_premium_discounts_invoice_id = None
    db_user.save()


@bot.message_handler(content_types=['text', 'photo'])
@message_error_handler
def accept_feedback(message):
    user = message.from_user
    db_user = models.BotUser.objects.get(user_id = user.id)

    if not db_user.feedback_enabled:
        bot.reply_to(message,
            global_preferences['texts__callback_blocked'],
            parse_mode='html'
        )
    else:
        if not db_user.dialogue.count():
            dialogue = models.FeedbackDialogue(
                user=db_user
            )
            dialogue.save()
        dialogue = models.FeedbackDialogue.objects.get(user=db_user)

        dialogue_data = ''

        if message.text:
            dialogue_data += '<div class="dialog-message user-message">\n'
            data_time = datetime.now().isoformat(sep=' ', timespec='seconds')
            dialogue_data += f'<div class="dialog-message-time">{data_time}</div>\n'
            dialogue_data += f'<div class="dialog-message-text">{html.escape(message.text)}</div>\n'
            dialogue_data += '</div>\n\n'

        else:
            dialogue_data += '<div class="dialog-message user-message">\n'
            data_time = datetime.now().isoformat(sep=' ', timespec='seconds')
            dialogue_data += f'<div class="dialog-message-time">{data_time}</div>\n'
            if message.caption:
                dialogue_data += f'<div class="dialog-message-text">{html.escape(message.caption)}</div>\n'
            photo = message.photo[-1]
            file = bot.get_file(photo.file_id)
            url = f'https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file.file_path}'
            length = 8
            path = ''
            for index in range(length):
                path += choice(ascii_lowercase)
            path = path + '.' + file.file_path.split('.')[-1]
            media = os.path.join(settings.MEDIA_ROOT, path)
            with open(media, 'wb') as f:
                response = get(url)
                f.write(response.content)
            if len(settings.ALLOWED_HOSTS) > 1:
                image_link = f'https://{settings.ALLOWED_HOSTS[1]}/media/{path}'
            else:
                image_link = f'https://{settings.ALLOWED_HOSTS[0]}/media/{path}'
            dialogue_data += f'<a class="dialog-image" href="{image_link}"><img src="{image_link}" /></a>\n'
            dialogue_data += '</div>\n\n'

        dialogue = models.FeedbackDialogue.objects.get(user=db_user)
        dialogue.data += dialogue_data
        dialogue.last_message_sender = 'user'
        dialogue.last_message_time = datetime.now(timezone.utc)
        dialogue.unread = True
        dialogue.save()

        bot.reply_to(message,
            global_preferences['texts__callback_accepted'],
            parse_mode='html'
        )


def format_shoe_sizes(offer, user_gender):
    if offer.offer_gender == 'male':
        min_size, max_size = MIN_MAN_SIZE, MAX_MAN_SIZE - 1
    elif offer.offer_gender == 'female':
        min_size, max_size = MIN_WOMAN_SIZE, MAX_WOMAN_SIZE - 1
    else:
        min_size = min(MIN_MAN_SIZE, MIN_WOMAN_SIZE)
        max_size = max(MAX_MAN_SIZE, MAX_WOMAN_SIZE) - 1

    sizes = []

    for size in range(min_size, max_size + 1):
        if getattr(offer, f'offer_size_{size}'):
            sizes.append(size)
        if getattr(offer, f'offer_size_{size}_5'):
            sizes.append(size + 0.5)

    if not sizes:
        return '-'

    if not user_gender:
        sizes = sizes
        sizes_type = 'EU'
    else:
        sizes_type = offer.offer_sizes_type
        if user_gender == 'male':
            if sizes_type == 'US':
                sizes = [size - 33 for size in sizes]
            elif sizes_type == 'UK':
                sizes = [size - 34 for size in sizes]
        else:
            if sizes_type == 'US':
                sizes = [size - 30 for size in sizes]
            elif sizes_type == 'UK':
                sizes = [size - 33 for size in sizes]

    beautiful_sizes = []
    sizes.append(1000)

    index = 0
    while index < len(sizes) - 1:
        left = sizes[index]
        while sizes[index + 1] - sizes[index] <= 0.51:
            index += 1
        right = sizes[index]

        if left == right:
            beautiful_sizes.append(f'{sizes_type} {left}')
        else:
            beautiful_sizes.append(f'{sizes_type} {left}-{right}')

        index += 1

    return ', '.join(beautiful_sizes)


def send_postponed_post(chat_id, gender, postponed_post):
    text = postponed_post.text
    if postponed_post.type == 'offer' and '{shoe_sizes}' in text:
        try:
            text = text.format(
                shoe_sizes=format_shoe_sizes(postponed_post, gender)
            )
        except:
            text = text.format(shoe_sizes='-')

    try:
        buttons = []
        for index in range(1, postponed_post.amount_of_buttons + 1):
            title = getattr(postponed_post, f'button_{index}_title')
            link = getattr(postponed_post, f'button_{index}_link')
            if title and link:
                buttons.append((title, link))
        if buttons:
            reply_markup = telebot.types.InlineKeyboardMarkup()
            for button in buttons:
                reply_markup.row(telebot.types.InlineKeyboardButton(
                    text=button[0], url=button[1]
                ))
        else:
            reply_markup = None
    except:
        reply_markup = None

    if postponed_post.image:
        image_link = f'https://{settings.ALLOWED_HOSTS[1]}/media/{postponed_post.image}'
        if postponed_post.image_place == 'bottom':
            text = f'<a href="{image_link}">&#8204;</a>' + text
            bot.send_message(chat_id,
                text=text,
                parse_mode='html',
                reply_markup=reply_markup
            )
        else:
            bot.send_photo(chat_id,
                photo=image_link,
                caption=text[:200],
                parse_mode='html',
                reply_markup=reply_markup
            )
    else:
        bot.send_message(chat_id,
            text=text,
            parse_mode='html',
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )


@require_POST
@csrf_exempt
def handle_bot_update(request):
    update_json_string = request.body.decode()
    update = telebot.types.Update.de_json(update_json_string)

    bot.process_new_updates([update])

    return HttpResponse()
