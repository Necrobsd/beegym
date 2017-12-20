# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 03:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_auto_20171208_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='photomessages',
            name='expiration_date',
            field=models.DateTimeField(blank=True, help_text='При заполнении данного поля, сообщение будет отправляться всем новым подписчикам, до указанной даты.\n Оставьте данное поле пустым, если хотите запустить одноразовую рассылку уже существующим подписчикам', null=True, verbose_name='Дата окончания рассылки'),
        ),
    ]