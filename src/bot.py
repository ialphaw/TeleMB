import telebot
from src.config import TOKEN, endpoint, herokuapi
from flask import Flask, request
import os


def init_and_start_bot():
    bot = telebot.TeleBot(TOKEN, threaded=False)
    server = Flask(__name__)
    users = {}

    @server.route('/' + TOKEN, methods=['POST'])
    def get_message():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=endpoint + TOKEN)
        return "!", 200

    @bot.message_handler(commands=['start'])
    def start_command(message):
        bot.send_message(message.chat.id, 'THE BOT IS ONLINE!')

    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
