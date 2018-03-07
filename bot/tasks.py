from celery import Celery
from django_telegrambot.apps import DjangoTelegramBot
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
                subs = message.group.subscribers.all()[4:]
                for counter, subscriber in enumerate(subs):
                    time.sleep(TIMEOUT)
                    if not counter:
                        try:
                            response = bot.sendPhoto(
                                subscriber.subscriber.chat_id,
                                # 472186134,
                                photo=image_url,
                                caption=message.text)
                            print(response)
                            file_id = response.photo[-1].file_id
                        except TelegramError as error:
                            print('Получен TelegramError: ', error.message)
                    else:
                        try:
                            response = bot.sendPhoto(
                                subscriber.subscriber.chat_id,
                                # 472186134,
                                photo=file_id if file_id else image_url,
                                caption=message.text)
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
