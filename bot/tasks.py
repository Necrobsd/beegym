from celery import Celery
from django_telegrambot.apps import DjangoTelegramBot
from telegram import ChatAction
from django.core.exceptions import ObjectDoesNotExist
from telegram.error import TelegramError
from . models import TextMessages, PhotoMessages
from django.conf import settings
from beegym.celery import app
import time


TIMEOUT = 1/25


#@app.task(bind=True, default_retry_delay=300, max_retries=3, time_limit=5 * 60)
@app.task()
def send_message(text_message=None, photo_message=None):
    try:
        bot = DjangoTelegramBot.get_bot()
        if photo_message:
            try:
                message = PhotoMessages.objects.get(id=photo_message)
                image_url = settings.DJANGO_TELEGRAMBOT.get('WEBHOOK_SITE') + message.image.url
                for counter, subscriber in enumerate(message.group.subscribers.all()):
                    time.sleep(TIMEOUT)
                    try:
                        response = bot.sendPhoto(
                            subscriber.subscriber.chat_id,
                            # 472186134,
                            photo=image_url,
                            caption=message.text if message.text else '')
                        print(response)
                    except TelegramError as error:
                        print('Получен TelegramError: ', error.message)
                message.status = True
                message.save()
            except ObjectDoesNotExist:
                pass

        if text_message:
            try:
                message = TextMessages.objects.get(id=text_message)
                text = '*{}*\n_{}_'.format(message.group.name, message.text)
                for subscriber in message.group.subscribers.all():
                    time.sleep(TIMEOUT)
                    try:
                        response = bot.sendMessage(
                            subscriber.subscriber.chat_id,
                            # 472186134,
                            text, parse_mode='Markdown')
                        print(response)
                    except TelegramError as error:
                        print('Получен TelegramError: ', error.message)
                message.status = True
                message.save()
            except ObjectDoesNotExist:
                pass
    except Exception as e:
        print('Ошибка: ', e)
        #raise self.retry(e)


@app.task
def send_adv(chat_id):
    time.sleep(60 * 2)
    bot = DjangoTelegramBot.get_bot()
    try:
        bot.send_chat_action(chat_id, action=ChatAction.TYPING)
    except TelegramError as error:
        print('Получен TelegramError: ', error.message)
    time.sleep(TIMEOUT)
    try:
        text = 'Понравился бот? Хочешь такого-же? Пиши сюда -> @AlexReznikoff'
        bot.send_message(chat_id, text=text)
    except TelegramError as error:
        print('Получен TelegramError: ', error.message)
