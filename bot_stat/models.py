from django.db import models
from bot.models import Groups
from bot.models import Subscribers


class SubscribersStats(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    group = models.ForeignKey(Groups, related_name='stats', verbose_name='Группа')
    count = models.IntegerField(verbose_name='Число подписчиков')

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

    def human_date(self):
        return '{}'.format(self.date.strftime('%d.%m.%Y'))


class UsedFunctions(models.Model):
    month = models.PositiveSmallIntegerField(verbose_name='Месяц', db_index=True)
    year = models.PositiveSmallIntegerField(verbose_name='Год', db_index=True)
    subscriber = models.ForeignKey(Subscribers,
                                   related_name='used_functions',
                                   on_delete=models.CASCADE,
                                   db_index=True)
    function = models.CharField(max_length=50, db_index=True)
    count = models.IntegerField(verbose_name='Количество вызовов', default=0)