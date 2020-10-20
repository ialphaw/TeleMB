import os
from threading import Thread
from time import sleep
import schedule

import telebot
from flask import Flask, request
from telegram import ChatPermissions

from src.config import TOKEN, endpoint


# server stuffs
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

    # -----------------------------------------------------------------------------

    # /start command
    @bot.message_handler(commands=['start'])
    def start_command(message):
        global chat_id
        f = False

        # find out if bot is admin or not
        admins = bot.get_chat_administrators(message.chat.id)
        for admin in admins:
            if admin.user.username == 'TeleMB_bot':
                f = True

        if f:
            chat_id = message.chat.id
            bot.send_message(message.chat.id, "The Bot Is Online")
        else:
            bot.send_message(message.chat.id, "Please Make The Bot Admin And Send /start Again")

    # -----------------------------------------------------------------------------

    # delete messages that include link
    @bot.message_handler(
        regexp="(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]["
               "a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,"
               "}|www\.[a-zA-Z0-9]+\.[^\s]{2,})")
    def handle_message(message):
        bot.delete_message(message.chat.id, message.message_id)

    # -----------------------------------------------------------------------------

    # if you are admin, you can restrict all members
    @bot.message_handler(commands=['mute'])
    def mute(message):
        f = False
        admins = bot.get_chat_administrators(message.chat.id)
        for admin in admins:
            if admin.user.id == message.from_user.id:
                f = True

        if f:
            bot.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=False))
            bot.send_message(message.chat.id, f"The Group Has Been Silenced By {message.from_user.username}")
        else:
            bot.reply_to(message, "Sorry, But You're Not Admin!")

    # -----------------------------------------------------------------------------

    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
