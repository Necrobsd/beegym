from celery import Celery
import time


app = Celery('tasks', broker='amqp://localhost')
TIMEOUT = 1/25


# @app.task
# def send(bot, message):
#     bot.sendMessage('')
