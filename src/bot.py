import os
from threading import Thread
from time import sleep

import schedule
import telebot
from flask import Flask, request
from telegram import ChatPermissions

from src.config import TOKEN, endpoint, wlc_msg, creators_id
from src.utils import is_start, read_info, write_info

info = read_info()

is_kicked = False

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
                if admin.user.username == 'TeleMB_bot':
                    f = True

            if f:
                info.append({'chat_title': message.chat.title})
                info[-1]['chat_id'] = message.chat.id
                info[-1]['start'] = True
                write_info(info)
                bot.send_message(message.chat.id, "The Bot Is Online")
            else:
                bot.send_message(message.chat.id, "Please Make The Bot Admin And Send /start Again")
        else:
            bot.reply_to(message, "The Bot Is Already Started")

    # -----------------------------------------------------------------------------

    # delete messages that include link
    @bot.message_handler(
        regexp="(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]["
               "a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,"
               "}|www\.[a-zA-Z0-9]+\.[^\s]{2,})")
    def handle_message(message):
        if is_start(info, message.chat.id):
            f = False
            admins = bot.get_chat_administrators(message.chat.id)
            for admin in admins:
                if admin.user.id == message.from_user.id:
                    f = True

            if not f:
                bot.delete_message(message.chat.id, message.message_id)
        else:
            bot.send_message(message.chat.id, 'Please Start The Bot First')

    # -----------------------------------------------------------------------------

    # if you are admin, you can restrict all members
    @bot.message_handler(commands=['mute'])
    def mute(message):
        if is_start(info, message.chat.id):
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
        else:
            bot.send_message(message.chat.id, 'Please Start The Bot First')

    # -----------------------------------------------------------------------------

    # if you are admin, you can un-restrict all members
    @bot.message_handler(commands=['un_mute'])
    def un_mute(message):
        if is_start(info, message.chat.id):
            bot.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=True))
            bot.send_message(message.chat.id, f"The Group Has Been Un-Silenced By {message.from_user.username}")
        else:
            bot.send_message(message.chat.id, 'Please Start The Bot First')

    # -----------------------------------------------------------------------------

    # delete joined messages and leave messages
    @bot.message_handler(content_types=["new_chat_members"])
    def delete_join_message(message):
        if is_start(info, message.chat.id):
            username = message.new_chat_members[0].username
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, f'Welcome @{username} :)')
            except:
                pass
        else:
            bot.send_message(message.chat.id, 'Please Start The Bot First')

    # -----------------------------------------------------------------------------

    # delete leave messages
    @bot.message_handler(content_types=['left_chat_member'])
    def delete_leave_message(message):
        global is_kicked
        if not is_kicked:
            if is_start(info, message.chat.id):
                username = message.left_chat_member.username
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, f'@{username} Left :(')
                except:
                    pass
            else:
                bot.send_message(message.chat.id, 'Please Start The Bot First')
        else:
            is_kicked = False

    # -----------------------------------------------------------------------------

    # show a help message
    @bot.message_handler(commands=['help'])
    def help_command(message):
        bot.send_message(message.chat.id, wlc_msg)

        # -----------------------------------------------------------------------------

    # kick a member by replying /kick to a message
    @bot.message_handler(commands=['kick'])
    def kick(message):
        global is_kicked
        if is_start(info, message.chat.id):
            f = False
            admins = bot.get_chat_administrators(message.chat.id)
            for admin in admins:
                if admin.user.id == message.from_user.id:
                    f = True

            if f:
                try:
                    kick_user = message.reply_to_message.from_user
                    is_kicked = True
                    bot.kick_chat_member(message.reply_to_message.chat.id, kick_user.id)
                    bot.send_message(message.chat.id,
                                     f'@{kick_user.username} Kicked By @{message.from_user.username}')
                except:
                    bot.reply_to(message, "Something Went Wrong")
            else:
                bot.reply_to(message, "Sorry, But You're Not Admin!")
        else:
            bot.send_message(message.chat.id, 'Please Start The Bot First')

    # -----------------------------------------------------------------------------

    # sends info to the creator only :)
    @bot.message_handler(commands=['send_info'])
    def send_info(message):
        user_id = message.from_user.id
        if user_id in creators_id:
            doc = open('info.txt', 'rb')
            try:
                bot.send_document(user_id, doc)
            except:
                pass
        else:
            bot.reply_to(message, 'You Have Not Access To This Command')

    # -----------------------------------------------------------------------------

    # mute the groups at 9:30 PM Teh
    def schedule_mute():
        for group in info:
            if is_start(info, group['chat_id']):
                bot.set_chat_permissions(group['chat_id'], ChatPermissions(can_send_messages=False))
                bot.send_message(group['chat_id'], 'Group Will Be Muted Till 8:30 AM')

    # ----------------------------------------------------------------------

    # mute the groups at 8:30 AM Teh
    def schedule_un_mute():
        for group in info:
            if is_start(info, group['chat_id']):
                bot.set_chat_permissions(group['chat_id'], ChatPermissions(can_send_messages=True))
                bot.send_message(group['chat_id'], 'Group Will Be Opened Till 9:30 PM')

    # ----------------------------------------------------------------------

    def schedule_checker():
        while True:
            schedule.run_pending()
            sleep(1)

    schedule.every().day.at("18:00").do(schedule_mute)
    schedule.every().day.at("05:00").do(schedule_un_mute)
    Thread(target=schedule_checker).start()

    # ----------------------------------------------------------------------

    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
