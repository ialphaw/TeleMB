import os
from threading import Thread
from time import sleep
import schedule

import telebot
from flask import Flask, request
from telegram import ChatPermissions

from src.config import TOKEN, endpoint, wlc_msg
from src.utils import is_start

info = []


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
        # check if bot isn't already started
        if not (is_start(info, message.chat.id)):
            f = False

            # find out if bot is admin or not
            admins = bot.get_chat_administrators(message.chat.id)
            for admin in admins:
                if admin.user.username == 'TeleMBTest_bot':
                    f = True

            if f:
                chat_id = message.chat.id
                info.append({'chat_id': chat_id})
                info[-1]['start'] = True
                print(info)
                bot.send_message(message.chat.id, "The Bot Is Online")
            else:
                bot.send_message(message.chat.id, "Please Make The Bot Admin And Send /start Againn")
        else:
            bot.reply_to(message, "The Bot Is Already Started")

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
            bot.send_message(message.chat.id, f"The Group Has Been Silenced By @{message.from_user.username}")
        else:
            bot.reply_to(message, "Sorry, But You're Not Admin!")

    # -----------------------------------------------------------------------------

    # if you are admin, you can un-restrict all members
    @bot.message_handler(commands=['un_mute'])
    def un_mute(message):
        bot.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=True))
        bot.send_message(message.chat.id, f"The Group Has Been Un-Silenced By @{message.from_user.username}")

    # -----------------------------------------------------------------------------

    # delete joined messages and leave messages
    @bot.message_handler(content_types=["new_chat_members"])
    def delete_join_message(message):
        username = message.new_chat_members[0].username
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f'Welcome @{username} :)')
        except:
            pass

    # -----------------------------------------------------------------------------

    # delete leave messages
    @bot.message_handler(content_types=['left_chat_member'])
    def delete_leave_message(message):
        username = message.left_chat_member.username
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f'@{username} Left :(')
        except:
            pass

    # -----------------------------------------------------------------------------

    # show a help message
    @bot.message_handler(commands=['help'])
    def help_command(message):
        bot.send_message(message.chat.id, wlc_msg)

    # -----------------------------------------------------------------------------

    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
