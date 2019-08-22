from datetime import date

from django import template
from django.conf import settings

from bot import models

register = template.Library()


@register.simple_tag
def unread_messages():
    amount = models.FeedbackDialogue.objects.filter(unread=True, ignored=False).count()

    if 11 <= amount <= 20:
        caption = 'непрочитанных диалогов'
    elif (amount % 10) == 1:
        caption = 'непрочитанный диалог'
    elif (amount % 10) <= 4:
        caption = 'непрочитанных диалога'
    else:
        caption = 'непрочитанных диалогов'

    if not amount:
        return ''
    else:
        return f'''<div><div style="display: inline-block; margin-bottom: 7px; padding: 8px 5px; line-height: normal; color: while; background: #55426e;">
В поддержке <b>{amount}</b> {caption}!
</div></div>
'''


@register.simple_tag
def men_size_amount(size):
    r_size = float(size)
    offers = models.PostponedPost.objects.filter(
        type='offer',
        status='done',
        offer_gender__in=['male', 'all'],
        sent=date.today()
    )

    amount = 0
    for offer in offers:
        if offer.offer_gender == 'male':
            min_size, max_size = settings.MIN_MAN_SIZE, settings.MAX_MAN_SIZE - 1
        elif offer.offer_gender == 'female':
            min_size, max_size = settings.MIN_WOMAN_SIZE, settings.MAX_WOMAN_SIZE - 1
        else:
            min_size = min(settings.MIN_MAN_SIZE, settings.MIN_WOMAN_SIZE)
            max_size = max(settings.MAX_MAN_SIZE, settings.MAX_WOMAN_SIZE) - 1
        sizes = []
        for size in range(min_size, max_size + 1):
            if getattr(offer, f'offer_size_{size}'):
                sizes.append(float(size))
            if getattr(offer, f'offer_size_{size}_5'):
                sizes.append(size + 0.5)
        if r_size in sizes:
            amount += 1

    return amount


@register.simple_tag
def women_size_amount(size):
    r_size = float(size)
    offers = models.PostponedPost.objects.filter(
        type='offer',
        status='done',
        offer_gender__in=['female', 'all'],
        sent=date.today()
    )

    amount = 0
    for offer in offers:
        if offer.offer_gender == 'male':
            min_size, max_size = settings.MIN_MAN_SIZE, settings.MAX_MAN_SIZE - 1
        elif offer.offer_gender == 'female':
            min_size, max_size = settings.MIN_WOMAN_SIZE, settings.MAX_WOMAN_SIZE - 1
        else:
            min_size = min(settings.MIN_MAN_SIZE, settings.MIN_WOMAN_SIZE)
            max_size = max(settings.MAX_MAN_SIZE, settings.MAX_WOMAN_SIZE) - 1
        sizes = []
        for size in range(min_size, max_size + 1):
            if getattr(offer, f'offer_size_{size}'):
                sizes.append(float(size))
            if getattr(offer, f'offer_size_{size}_5'):
                sizes.append(size + 0.5)
        if r_size in sizes:
            amount += 1

    return amount
