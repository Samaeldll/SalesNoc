from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from telebot import TeleBot

from django_telegram_login.widgets.constants import (
    SMALL,
    MEDIUM,
    LARGE,
    DISABLE_USER_PHOTO,
)
from django_telegram_login.widgets.generator import (
    create_callback_login_widget,
    create_redirect_login_widget,
)
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import (
    NotTelegramDataError,
    TelegramDataIsOutdatedError,
)

# Объявление переменной бота
bot_name = settings.TELEGRAM_BOT_NAME
bot = TeleBot(settings.TELEGRAM_BOT_API_KEY, threaded=False)

# Название класса обязательно - "Command"
class Command(BaseCommand):
  	# Используется как описание команды обычно
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot.enable_save
        _next_step_handlers(delay=2) # Сохранение обработчиков
        bot.load_next_step_handlers()								# Загрузка обработчиков

def index(request):

    # Initially, the index page may have no get params in URL
    # For example, if it is a home page, a user should be redirected from the widget
    if not request.GET.get('hash'):
        return HttpResponse('Handle the missing Telegram data in the response.')

    try:
        result = verify_telegram_authentication(
            bot_token=bot_token, request_data=request.GET
        )

    except TelegramDataIsOutdatedError:
        return HttpResponse('Authentication was received more than a day ago.')

    except NotTelegramDataError:
        return HttpResponse('The data is not related to Telegram!')

    # Or handle it like you want. For example, save to DB. :)
    return HttpResponse('Hello, ' + result['first_name'] + '!')


def callback(request):
    telegram_login_widget = create_callback_login_widget(bot_name, size=SMALL)

    context = {'telegram_login_widget': telegram_login_widget}
    return render(request, 'telegram_auth/callback.html', context)


def redirect(request):
    telegram_login_widget = create_redirect_login_widget(
        redirect_url, bot_name, size=LARGE, user_photo=DISABLE_USER_PHOTO
    )

    context = {'telegram_login_widget': telegram_login_widget}
    return render(request, 'telegram_auth/redirect.html', context)

@bot.message_handler(commands=['start', 'go'])
def get_text_messages(message):
    bot.send_message(message.chat.id, 'Приветствую тебя, давай авторизуемся?')

bot.delete_webhook()
bot.polling(none_stop=True)