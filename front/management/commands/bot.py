from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from telebot import TeleBot
import sys
sys.path.append('front/')
from front.models import (
    Contract,
    FrontUser,
    User,
)

bot_name = settings.TELEGRAM_BOT_NAME
bot = TeleBot(settings.TELEGRAM_BOT_API_KEY, threaded=False)


@bot.message_handler(commands=['start', 'go'])
def get_text_messages(message):
    bot.send_message(message.chat.id, 'Приветствую тебя, давай авторизуемся?')

bot.delete_webhook()
bot.polling(none_stop=True)