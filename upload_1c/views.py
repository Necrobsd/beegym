from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate


# Create your views here.
@csrf_exempt
def upload_cards(request):
    user = None
    if "HTTP_AUTHORIZATION" in request.META:
        auth = request.META["HTTP_AUTHORIZATION"].split()
        if len(auth) == 2 and auth[0].lower() == "basic":
            data = base64.b64decode(auth[1])
            username, password = data.decode().split(":")
            user = authenticate(username=username, password=password)
            if user and user.is_active():
                print('Пользователь успешно вошел:', user)
                print('Список переданных файлов: ', request.FILES)
                try:
                    file = request.FILES['file']
                    path = default_storage.save(str(file), ContentFile(file.read()))
                    return HttpResponse('ok')
                except KeyError:
                    HttpResponse('You should send JSON file with key "file" (For example: file=my_file.json')

    # Если не авторизовали — даем ответ с 401, требуем авторизоваться
    if user is None or not user.is_active:
        response = HttpResponse()
        response.status_code = 401
        response["WWW-Authenticate"] = 'Basic realm="Private area"'
        return response
