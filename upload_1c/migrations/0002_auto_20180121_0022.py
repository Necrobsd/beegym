# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-20 14:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_1c', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cards',
            name='card_number',
            field=models.SmallIntegerField(db_index=True, unique=True, verbose_name='Номер карты'),
        ),
    ]