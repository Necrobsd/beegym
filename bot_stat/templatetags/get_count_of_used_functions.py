from django import template

register = template.Library()


@register.filter(name='get_count')
def get_count(subscriber, function):
    try:
        print(subscriber, 'function =', function)
        print('result_count=', subscriber.get(function=function).count)
        return subscriber.get(function=function).count
    except:
        return 0
