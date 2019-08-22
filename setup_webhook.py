import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salefinder_development.settings")
django.setup()

from time import sleep

import telebot

from django.conf import settings


if __name__ == '__main__':
    bot = telebot.TeleBot(settings.BOT_TOKEN, threaded=False)

    webhook_url = f'https://{settings.ALLOWED_HOSTS[1]}/{settings.BOT_TOKEN}'

    try:
        bot.remove_webhook()
        sleep(0.5)
        print(bot.set_webhook(url=webhook_url))
    except BaseException as error:
        print(error)
