# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-26 05:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_1c', '0004_auto_20180122_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cards',
            name='exp_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания абонемента'),
        ),
    ]
