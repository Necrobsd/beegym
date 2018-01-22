from django import template
from bot_stat.models import UsedFunctions


register = template.Library()


@register.filter(name='get_count')
def get_count(subscriber, function):
    try:
        print(subscriber, 'function =', function)
        print('result_count=', subscriber.get(function=function).count)
        return subscriber.get(function=function).count
    except:
        return 0


@register.simple_tag()
def get_total_count(function):
    count = 0
    try:
        for f in UsedFunctions.objects.filter(function=function):
            count += f.count
    except:
        pass
    return count
