from django import forms
from .models import SubscribersStats
from datetime import datetime

first_year = SubscribersStats.objects.first().date.year
last_year = SubscribersStats.objects.last().date.year + 1
years = [(year, year) for year in range(first_year, last_year)]
months = [('1', 'январь'),
          ('2', 'февраль'),
          ('3', 'март'),
          ('4', 'апрель'),
          ('5', 'май'),
          ('6', 'июнь'),
          ('7', 'июль'),
          ('8', 'август'),
          ('9', 'сентябрь'),
          ('10', 'октябрь'),
          ('11', 'ноябрь'),
          ('12', 'декабрь')]
current_year = datetime.now().year
current_month = datetime.now().month


class DateForm(forms.Form):
    month = forms.ChoiceField(label='Выберите дату',
                              choices=months,
                              initial=current_month)
    year = forms.ChoiceField(choices=years,
                             initial=current_year)
