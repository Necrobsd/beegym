# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-06 03:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bot', '0003_auto_20171205_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscribersStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Дата')),
                ('count', models.IntegerField(verbose_name='Число подписчиков')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='bot.Groups', verbose_name='Группа')),
            ],
            options={
                'verbose_name': 'Статистика',
                'verbose_name_plural': 'Статистика',
            },
        ),
    ]
