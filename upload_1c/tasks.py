from beegym.celery import app
import json
from django.core.exceptions import ObjectDoesNotExist
from .models import Cards


@app.task()
def load_to_db(file):
    data = json.load(open(file, 'r'))
    for card_number, values in data:
        try:
            card = Cards.objects.get(card_number)
            card.exp_date = values['exp_date']
            card.is_active = values['is_active']
            card.name = values['name']
            card.save()
        except ObjectDoesNotExist:
            card = Cards.objects.create(
                card_number=card_number,
                exp_date=values['exp_date'],
                is_active=values['is_active'],
                name=values['name'])