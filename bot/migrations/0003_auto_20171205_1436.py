# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-05 04:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_welcometext'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photomessages',
            name='image',
            field=models.ImageField(help_text='Максимальный размер - 5 Мб', upload_to='messages_img', verbose_name='Изображение'),
        ),
    ]
