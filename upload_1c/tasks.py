from beegym.celery import app
import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from .models import Cards
import os


# @app.task()
def load_to_db(filename):
    file = os.path.join(default_storage.location, filename)
    if os.path.exists(file) and os.path.isfile(file):
        print('Получен файл = ', file)
        with open(file, 'r') as f:
            data = json.load(f)
            for card_number, values in data.items():
                if values['name']:
                    # print(card_number, 'Дата истечения абонемента: ', values['exp_date'], 'Название абонемента: ', values['name'])

                    try:
                        card = Cards.objects.get(card_number)

                        if card.exp_date != values['exp_date']:
                            card.exp_date = values['exp_date']
                            card.is_active = values['is_active']
                            card.name = values['name']
                            card.save()
                    except ObjectDoesNotExist:
                        Cards.objects.create(
                            card_number=card_number,
                            exp_date=values['exp_date'],
                            is_active=values['is_active'],
                            name=values['name'])
        # print('Сохранение данных в базу завершено. Удаляем полученный файл ', file)
        # os.remove(file)
    else:
        print('Ошибка чтения полученного файла = ', file)
