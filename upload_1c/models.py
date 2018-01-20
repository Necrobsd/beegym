from django.db import models


# Create your models here.
class Cards(models.Model):
    card_number = models.SmallIntegerField(verbose_name='Номер карты',
                                           unique=True, db_index=True)
    exp_date = models.DateField(verbose_name='Дата окончания абонемента',
                                blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Активация абонемента',
                                    default=False)
    name = models.CharField(verbose_name='Название абонемента',
                            blank=True, null=True, max_length=100)

    class Meta:
        verbose_name = 'карта клиента'
        verbose_name_plural = 'карты клиентов'

    def __str__(self):
        return self.card_number
