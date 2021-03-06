from beegym.celery import app
import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from .models import Cards
import os
from chardet.universaldetector import UniversalDetector
import pytz
from datetime import datetime


local_tz = pytz.timezone("Asia/Vladivostok")
utc_tz = pytz.utc


def transform_to_date(date_str):
    if date_str:
        date_str += ' 23:59:59'
        date = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
        return local_tz.localize(date)
    else:
        return None


# @app.task()
def load_to_db(filename):
    file = os.path.join(default_storage.location, filename)
    if os.path.exists(file) and os.path.isfile(file):
        print('Получен файл: ', file)
        detector = UniversalDetector()
        detector.reset()
        for line in open(file, 'rb'):
            detector.feed(line)
            if detector.done: break
        detector.close()
        enc = detector.result['encoding'] if detector.result['encoding'] else 'utf-8'
        print('Кодировка:', detector.result['encoding'])
        with open(file, 'r', encoding=enc) as f:
            data = json.load(f)
            for card_number, values in data.items():
                if values['name']:
                    if values['name'].lower().find("разовый") == -1:
                    # print(card_number, 'Дата истечения абонемента: ',
                    #       values['exp_date'], 'Название абонемента: ', values['name'])
                        try:
                            card = Cards.objects.get(card_number=card_number)
                            if card.exp_date != transform_to_date(values['exp_date']):
                                card.exp_date = transform_to_date(values['exp_date'])
                                card.is_active = values['is_active']
                                card.name = values['name']
                                card.save()
                        except ObjectDoesNotExist:
                            Cards.objects.create(
                                card_number=card_number,
                                exp_date=transform_to_date(values['exp_date']),
                                is_active=values['is_active'],
                                name=values['name'])
        # print('Сохранение данных в базу завершено. Удаляем полученный файл ', file)
        # os.remove(file)
    else:
        print('Ошибка. Полученный файл не существует или не является файлом: ', file)
