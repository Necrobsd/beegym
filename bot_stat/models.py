from django.db import models
from bot.models import Groups


class SubscribersStats(models.Model):
    date = models.DateTimeField(verbose_name='Дата')
    group = models.ForeignKey(Groups, related_name='stats', verbose_name='Группа')
    count = models.IntegerField(verbose_name='Число подписчиков')

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

    def human_date(self):
        return '{}'.format(self.date.strftime('%d.%m.%Y'))