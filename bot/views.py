from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django_telegrambot.apps import DjangoTelegramBot
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


# Create your views here.
def index(request):
    bot_list = DjangoTelegramBot.bots
    context = {'bot_list': bot_list, 'update_mode':settings.DJANGO_TELEGRAMBOT['MODE']}
    return render(request, 'bot/index.html', context)


@csrf_exempt
def upload_cards(request):
    if "HTTP_AUTHORIZATION" in request.META:
        auth = request.META["HTTP_AUTHORIZATION"].split()
        if len(auth) == 2 and auth[0].lower() == "basic":
            data = base64.b64decode(auth[1])
            username, password = data.decode().split(":")
            print(username, password)
    else:
        print('NO')
    print(request.FILES)
    file = request.FILES['file']
    path = default_storage.save(str(file), ContentFile(file.read()))
    return HttpResponse('ok')