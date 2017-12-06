from django.shortcuts import render, render_to_response
from chartit import DataPool, Chart
from . models import SubscribersStats
from datetime import datetime
from bot.models import Groups
from pprint import pprint


def get_stats(request):
    if request.GET:
        date = datetime.strptime(request.GET.get('date'), '%Y-%m')
        print(date)
    groups = Groups.objects.all()
    series = [{'options': {'source': SubscribersStats.objects.filter(group=group)},
               'terms': [
                   {'date{}'.format(group.id): 'human_date'},
                   {'{}'.format(group.name): 'count'}
               ]} for group in groups]
    terms = {'date{}'.format(group.id): ['{}'.format(group.name)] for group in groups}
    # pprint(series)
    # data = [SubscribersStats.objects.filter(date__lte=datetime(2017, 11, 5)]
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
    pprint(series[1]['terms'][0].keys())
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
                'text': 'Количество подписчиков'
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

    # Step 3: Send the chart object to the template.
    return render_to_response('bot_stat/bot_stat.html', {'stats': cht})
