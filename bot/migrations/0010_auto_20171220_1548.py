# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-20 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_auto_20171220_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribers',
            name='mailing_group',
            field=models.TextField(blank=True, max_length=100, null=True, verbose_name='Группа для создания рассылки'),
        ),
        migrations.AlterField(
            model_name='subscribers',
            name='subscribing_status',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Статус'),
        ),
    ]
