from django import template
from django.utils import timezone
from datetime import datetime
from debate.templatetags.arabic_number import arabic_number

register = template.Library()

@register.filter(name='remaining_datetime')
def remaining_datetime(value):

    current_datetime = timezone.now()
    remaining = current_datetime - value

    if remaining.days == 0:
        hours_counter = 0
        stricked_remaining_seconds = remaining.seconds
        
        if stricked_remaining_seconds >= 3600:
            hours_counter += 1
            stricked_remaining_seconds -= 3600

        if hours_counter >= 1:
            total = hours_counter
            if total < 0:
                total *= -1
            remaining = 'منذ' + ' ' + str(total) + ' ' + 'من الساعات'

        elif remaining.seconds < 3600:
            total = remaining.seconds/60
            if total < 0:
                total *= -1
            remaining = 'منذ' + ' ' + str(total).split('.')[0] + ' ' + 'من الدقائق'
        
    else:
        total = remaining.days
        if total < 0:
            total *= -1
        remaining = 'منذ' + ' ' + str(total) + ' ' + 'من الايام'

    return remaining
