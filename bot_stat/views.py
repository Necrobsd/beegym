from django.shortcuts import render, render_to_response
from chartit import DataPool, Chart
from . models import SubscribersStats, UsedFunctions
from django.contrib.auth.decorators import login_required
from bot.models import Groups, Subscribers
from .forms import DateForm, current_month, current_year


@login_required(login_url='admin:login')
def get_stats(request):
    form = DateForm()
    groups = Groups.objects.all()
    series = [{'options': {'source': SubscribersStats.objects.filter(group=group,
                                                                     date__year=current_year,
                                                                     date__month=current_month)},
               'terms': [
                   {'date{}'.format(group.id): 'human_date'},
                   {'{}'.format(group.name): 'count'}
               ]} for group in groups]
    if request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            series = [{'options': {'source': SubscribersStats.objects.filter(group=group,
                                                                             date__year=year,
                                                                             date__month=month)},
                       'terms': [
                           {'date{}'.format(group.id): 'human_date'},
                           {'{}'.format(group.name): 'count'}
                       ]} for group in groups]
    terms = {'date{}'.format(group.id): ['{}'.format(group.name)] for group in groups}
    ds = DataPool(
        series=series
        # [
        #     {
        #         'options': {
        #             'source': SubscribersStats.objects.filter(group_id=1)
        #         },
        #         'terms': ['date', 'count']
        #     },
        #     {
        #         'options': {
        #             'source': SubscribersStats.objects.filter(group_id=2)
        #         },
        #         'terms': [{'date_two': 'date'}, {'count_two': 'count'}]
        #     },
        #     {
        #         'options': {
        #             'source': SubscribersStats.objects.filter(group_id=6)
        #         },
        #         'terms': [{'date_three':'date'}, {'count_three': 'count'}]
        #     }
        #
        # ]
    )
    # terms = {each['terms'][0].k: [each['terms'][1]] for each in series}
    # pprint(series[1]['terms'][0].keys())
    cht = Chart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'line',
                'stacking': False,
            },
             'terms': terms
             #     {
             #     'date1': ['count1'],
             #     'date2': ['count2'],
             #     'date3': ['count3']
             # }
            }],
        chart_options={
            'title': {
                'text': 'Статистика по подписчикам'
            },
            'xAxis': {
                'title': {
                    'text': 'Дата'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Подписчики'
                }
            }
        },
    )

    subscribers = Subscribers.objects.all()
    return render(request, 'bot_stat/bot_stat.html', {'stats': cht,
                                                      'form': form,
                                                      'subscribers': subscribers})
