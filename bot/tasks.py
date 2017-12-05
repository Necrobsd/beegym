from celery import Celery
from django_telegrambot.apps import DjangoTelegramBot
from telegram.error import TelegramError
from . models import TextMessages, PhotoMessages
from django.conf import settings
import time


app = Celery('tasks', broker='amqp://localhost')
TIMEOUT = 1/25


@app.task(bind=True, default_retry_delay=300, max_retries=5)
def send_message(message):
    try:
        bot = DjangoTelegramBot.get_bot()
        if message.image:
            image_url = settings.DJANGO_TELEGRAMBOT.get('WEBHOOK_SITE') + message.image.url
            print('IMAGE_URL=', image_url)
            for counter, subscriber in enumerate(message.group.subscribers.all()):
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
                        print(error.message)
                else:
                    bot.sendPhoto(
                        subscriber.subscriber.chat_id,
                        # 472186134,
                        photo=file_id if file_id else image_url,
                        caption=message.text)
            message.status = True
            message.save()
        else:
            for subscriber in message.group.subscribers.all():
                time.sleep(TIMEOUT)
                try:
                    response = bot.sendMessage(
                        subscriber.subscriber.chat_id,
                        # 472186134,
                        message.text)
                    print(response)
                except TelegramError as error:
                    print(error.message)
            message.status = True
            message.save()

    except Exception as e:
        print("maybe do some clenup here....")
        self.retry(e)
