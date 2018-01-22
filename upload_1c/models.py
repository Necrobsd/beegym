from django.db import models


# Create your models here.
class Cards(models.Model):
    card_number = models.CharField(verbose_name='Номер карты',
                                   max_length=6, unique=True, db_index=True)
    exp_date = models.CharField(verbose_name='Дата окончания абонемента',
                                max_length=10, blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Активация абонемента',
                                    default=False)
    name = models.CharField(verbose_name='Название абонемента',
                            blank=True, null=True, max_length=100)

    class Meta:
        verbose_name = 'карта клиента'
        verbose_name_plural = 'карты клиентов'

    def __str__(self):
        return self.card_number
