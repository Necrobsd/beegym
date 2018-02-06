from django.shortcuts import render, HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate
from .tasks import load_to_db
import json
import os
from django.utils.timezone import localtime, now
from django.core.files.base import ContentFile


# Create your views here.
@csrf_exempt
def upload_cards(request):
    user = None
    if "HTTP_AUTHORIZATION" in request.META:
        auth = request.META["HTTP_AUTHORIZATION"].split()
        if len(auth) == 2 and auth[0].lower() == "basic":
            try:
                data = base64.b64decode(auth[1])
                username, password = data.decode().split(":")
                user = authenticate(username=username, password=password)
            except:
                pass
            if user and user.is_active:
                print('Пользователь успешно вошел:', user)
                print('Список переданных файлов: ', request.FILES)
                try:
                    file = request.FILES['file']
                    upload_date = localtime(now()).strftime("%d-%m-%Y_%H-%M-%S")
                    filename = default_storage.save('upload_{}_{}'.format(upload_date, str(file)),
                                                    ContentFile(file.read()))
                    load_to_db(filename)
                    return HttpResponse('ok')
                # except (KeyError, ValueError):
                    # return HttpResponse('You should send JSON file with key "file" (For example: file=my_file.json)')
                # try:
                #     data = json.load(file)
                except Exception as e:
                    print('JSON file errors: {}'.format(e))
                    return HttpResponseBadRequest('JSON file errors: {}'.format(e))
                # filename = '{}_1C.json'.format(localtime(now()).strftime("%d-%m-%Y_%H-%M-%S"))
                # with open(os.path.join(default_storage.location, filename), 'w', encoding='utf8') as f:
                #     json.dump(data, f, ensure_ascii=False)
                # load_to_db(filename)
                # return HttpResponse('ok')

    # Если не авторизовали — даем ответ с 401, требуем авторизоваться
    if user is None or not user.is_active:
        response = HttpResponse()
        response.status_code = 401
        response["WWW-Authenticate"] = 'Basic realm="Private area"'
        return response
