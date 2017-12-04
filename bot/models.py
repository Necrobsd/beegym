from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):
    if not instance.is_staff:
        instance.is_staff = True
        try:
            management_group = Group.objects.get(name='management')
            if management_group not in instance.groups.all():
                instance.groups.add(management_group)
                print('OK')
        except ObjectDoesNotExist:
            pass
        instance.save()



STATUSES = [
    ('sub', 'подписка'),
    ('unsub', 'отписка')
]


class Subscribers(models.Model):
    chat_id = models.IntegerField(unique=True, verbose_name='Идентификатор пользователя')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Имя пользователя')
    subscribing_status = models.CharField(max_length=5, choices=STATUSES, verbose_name='В процессе подписки', blank=True, null=True)

    class Meta:
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'

    def __str__(self):
        return self.name + ', id: ' + str(self.chat_id)


class Groups(models.Model):
    name = models.CharField(unique=True, verbose_name='Название группы', max_length=100)
    description = models.TextField(max_length=255, verbose_name='Описание группы', null=True, blank=True)
    is_default = models.BooleanField(
        default=False,
        verbose_name='Группа по-умолчанию'
    )

    class Meta:
        verbose_name = 'группа рассылки'
        verbose_name_plural = 'группы рассылки'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            groups = Groups.objects.exclude(id=self.id)
            for group in groups:
                group.is_default = False
                group.save()
        super(Groups, self).save(*args, **kwargs)


class SubscribersInGroups(models.Model):
    subscriber = models.ForeignKey(Subscribers, related_name='groups', on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, related_name='subscribers', on_delete=models.CASCADE)
    subscribition_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки в группу')

    class Meta:
        unique_together = (('subscriber', 'group'),)
        verbose_name = 'подписчики в группах'
        verbose_name_plural = 'подписчики в группах'


class Messages(models.Model):
    group = models.ForeignKey(Groups, related_name='messages',
                              verbose_name='Группа для рассылки')
    image = models.ImageField(upload_to='messages_img',
                              verbose_name='Картинка',
                              null=True, blank=True,
                              help_text='Максимальный размер - 5 Мб')
    text = models.TextField(max_length=200, verbose_name='Текст сообщения',
                            help_text='Максимум 200 символов')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания')
    status = models.BooleanField(default=False, verbose_name='Отправлено', editable=False)

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'

    def __str__(self):
        return 'Сообщение {}'.format(self.pk)

