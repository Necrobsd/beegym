from django import forms
from .models import SubscribersStats
from datetime import datetime


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


class DateForm(forms.Form):
    month = forms.ChoiceField(label='Выберите дату',
                              choices=months,
                              initial=datetime.now().month)
    year = forms.ChoiceField(choices=[(year, year)
                                      for year in range(SubscribersStats.objects.first().date.year,
                                                        SubscribersStats.objects.last().date.year + 1)],
                             initial=datetime.now().year)
