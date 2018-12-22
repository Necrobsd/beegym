import time

from telegram import ChatAction
from uwsgi_tasks import task, TaskExecutor

default_app_config = "bot.apps.BotConfig"


@task(executor=TaskExecutor.SPOOLER)
def send_adv_message(chat_id, bot):
    """Функция отправки новым пользователям рекламного сообщения"""
    time.sleep(60 * 2)  # Ждем две минуты после начала работы с ботом
    try:
        bot.send_chat_action(chat_id, action=ChatAction.TYPING)  # Отправка статуса о наборе сообщения
    except:
        pass
    time.sleep(5)
    try:
        bot.sendMessage(chat_id, text='Понравился бот? Хочешь такого-же? Пиши сюда -> @AlexReznikoff')
    except:
        pass
