import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salefinder_development.settings")
django.setup()

from time import sleep
from datetime import datetime, timezone, date

from django.conf import settings

from bot import models
from bot.views import send_postponed_post


def process_statuses():
    now = datetime.now(timezone.utc)

    expired_postponed_posts = models.PostponedPost.objects.filter(
        status='postponed', postpone_time__lte=now
    )

    for expired_postponed_post in expired_postponed_posts:
        print(expired_postponed_post.created)
        try:
            expired_postponed_post.status = 'queue'
            expired_postponed_post.save()
        except BaseException as error:
            print(f'{type(error)}: {error}')


def process_postponed_post(postponed_post):
    print(postponed_post.created)
    postponed_post.status = 'process'
    postponed_post.save()

    if postponed_post.type == 'post':
        temp_users = list(models.BotUser.objects.all())

        users = []

        for user in temp_users:
            if postponed_post.post_all:
                users.append(user)
            elif postponed_post.post_need_spam_setup and not user.configured:
                users.append(user)
            elif postponed_post.post_0_referrals and user.amount_of_referrals == 0:
                users.append(user)
            elif postponed_post.post_1_referrals and user.amount_of_referrals == 1:
                users.append(user)
            elif postponed_post.post_2_referrals and user.amount_of_referrals == 2:
                users.append(user)
            elif postponed_post.post_3_and_more_referrals and user.amount_of_referrals >= 3:
                users.append(user)

    elif postponed_post.type == 'offer':
        if postponed_post.offer_gender == 'male':
            genders = ['male', None]
        elif postponed_post.offer_gender == 'female':
            genders = ['female', None]
        else:
            genders = ['male', 'female', None]

        if postponed_post.offer_premium:
            premium_statuses = [True]
        else:
            premium_statuses = [True, False]

        if postponed_post.offer_gender == 'male':
            min_size, max_size = settings.MIN_MAN_SIZE, settings.MAX_MAN_SIZE - 1
        elif postponed_post.offer_gender == 'female':
            min_size, max_size = settings.MIN_WOMAN_SIZE, settings.MAX_WOMAN_SIZE - 1
        else:
            min_size = min(settings.MIN_MAN_SIZE, settings.MIN_WOMAN_SIZE)
            max_size = max(settings.MAX_MAN_SIZE, settings.MAX_WOMAN_SIZE) - 1
        sizes = []
        for size in range(min_size, max_size + 1):
            if getattr(postponed_post, f'offer_size_{size}'):
                sizes.append(float(size))
            if getattr(postponed_post, f'offer_size_{size}_5'):
                sizes.append(size + 0.5)
        sizes = set(sizes)

        print(genders)
        print(premium_statuses)
        print(sizes)

        users = list(models.BotUser.objects.all())
        users = [user for user in users if (bool(user.is_premium()) in premium_statuses and user.gender in genders)]
        users = [user for user in users if ((not user.configured) or (set(user.float_sizes()) & sizes))]

    amount_of_receivers = 0

    for user in users:
        print(user.username)
        try:
            send_postponed_post(user.user_id, user.gender, postponed_post)
        except BaseException as error:
            print(f'{type(error)}: {error}')
        else:
            amount_of_receivers += 1
    print(amount_of_receivers)

    postponed_post.status = 'done'
    postponed_post.sent = date.today()
    postponed_post.amount_of_receivers = amount_of_receivers
    postponed_post.save()


if __name__ == '__main__':
    while True:
        try:
            print('Process statuses')
            process_statuses()
        except BaseException as error:
            print(f'{type(error)}: {error}')
        finally:
            print()

        try:
            postponed_post = models.PostponedPost.objects.filter(
                status='queue'
            ).order_by('created').first()
            if postponed_post:
                print('Process post')
                process_postponed_post(postponed_post)
        except BaseException as error:
            print(f'{type(error)}: {error}')
        finally:
            print()

        sleep(1)
