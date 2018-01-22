from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


# Основыне настройки Django для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beegym.settings')

app = Celery('beegym', broker='amqp://localhost')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'save-subscribers-statistics': {
        'task': 'bot_stat.tasks.save_stat',
        'schedule': crontab(minute=58, hour=13), # В 23-58 каждый день считаем
                                                 # статистику пользователей
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))