from bot.models import Groups
from .models import SubscribersStats
from beegym.celery import app


@app.task
def save_stat():
    for group in Groups.objects.all():
        SubscribersStats.objects.create(group=group, count=group.subscribers.all().count())
