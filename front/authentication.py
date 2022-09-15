from django_telegram_login.authentication import verify_telegram_authentication
from django.conf import settings
from django.http import HttpResponse
from .models import (
    FrontUser,
    User
)
from django_telegram_login.errors import (
    NotTelegramDataError,
    TelegramDataIsOutdatedError,
)

bot_token = settings.TELEGRAM_BOT_API_KEY

def index(request):

    if not request.GET.get('hash'):
        return HttpResponse('Обрабатывать недостающие данные телеграммы в ответе')

    try:
        result = verify_telegram_authentication(bot_token=bot_token, request_data=request.GET)

    except TelegramDataIsOutdatedError:
        return HttpResponse('Аутентификация получена более суток назад')

    except NotTelegramDataError:
        return HttpResponse('Данные не относятся к телеграмму')

    #save to DB.
    request.user.id_telegram = result['id']
    request.user.login_telegram = result['username']
    request.user.save()
    return HttpResponse('Приветствую, ' + result['username'] + ' авторизация прошла успешно! ')