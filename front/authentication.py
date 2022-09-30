from django_telegram_login.authentication import verify_telegram_authentication
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
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
    if not FrontUser.objects.filter(id_telegram=result['id']).exists():
            request.user.id_telegram = result['id']
            request.user.login_telegram = result['username']
            request.user.save()
            messages.add_message(request, messages.SUCCESS, result['username'] + " вы успешно авторизированы! ")
            return redirect("profile")

    messages.add_message(
        request,
        messages.SUCCESS, " Данный пользователь уже используется, уберите привязку в telegram или обратитесь к администратору. ")
    return redirect("profile")
    #return HttpResponse('Приветствую, ' + result['username'] + ' авторизация прошла успешно! ')