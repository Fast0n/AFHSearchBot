#!/usr/bin/python3.6
from bs4 import BeautifulSoup
from settings import token, start_msg, client_file, keypad, typepad, type_
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
import os
import json
import re
import requests
import sys
import telepot

# State for user
user_state = {}

command = {}
search = {}
tipo = {}
markup = ReplyKeyboardMarkup(keyboard=keypad)
markup1 = ReplyKeyboardMarkup(keyboard=typepad)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    command_input = msg['text']

    # Check user state
    try:
        user_state[chat_id] = user_state[chat_id]
    except:
        user_state[chat_id] = 0

    # start command
    if command_input == "/start":
        if register_user(chat_id):
            bot.sendMessage(chat_id, start_msg, parse_mode='Markdown')
            command_input = "/find"

    elif command_input == '/dona':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Dona", url='https://paypal.me/Fast0n/')],
        ])
        bot.sendMessage(chat_id, "Codice sorgente: \n" +
                        "[AFHSearchBot](https://github.com/Fast0n/AFHSearchBot)\n\n" +
                        "Sviluppato da: \n" +
                        "[Fast0n](https://github.com/Fast0n)\n\n" +
                        "🍺 Se sei soddisfatto offrimi una birra 🍺", parse_mode='Markdown', reply_markup=keyboard)
        user_state[chat_id] = 0

    elif command_input == '/find' or command_input == '/direct':
        command[chat_id] = command_input
        bot.sendMessage(chat_id, "Cosa stai cercando?", reply_markup=markup1)
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        tipo[chat_id] = command_input
        bot.sendMessage(chat_id, "Nome " + type_[command_input],
                        reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        user_state[chat_id] = 2

    elif user_state[chat_id] == 2 and command[chat_id] == '/find':
        search[chat_id] = command_input
        bot.sendMessage(
            chat_id, "Quanti file vuoi visualizzare? (Solo numeri)", reply_markup=markup)
        user_state[chat_id] = 3

    elif user_state[chat_id] == 3 or command[chat_id] == '/direct':
        if command[chat_id] == '/direct':
            search[chat_id] = command_input
        else:
            try:
                if int(command_input) > 15 or int(command_input) == 0:
                    print(command_input)
            except ValueError:
                bot.sendMessage(
                    chat_id, "Quanti file vuoi visualizzare? (Solo numeri)", reply_markup=markup)
                return

        link = "https://www.androidfilehost.com/?w=search&s=" + search[chat_id].lower().replace(" ", "-") + \
            "&type=" + tipo[chat_id]
        URL = "https://afhsearch-api.herokuapp.com/" + "?search= " + \
            search[chat_id].replace(' ', '%20') + "&type=" + tipo[chat_id]

        r = requests.get(URL, allow_redirects=True)

        try:
            json_data = json.loads(r.text)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Scopri di più',
                                    url=link)],
            ])
            bot.sendMessage(chat_id, "Ho cercando: \n`" +
                            link + "`", parse_mode='Markdown', reply_markup=keyboard)
            for key in json_data.keys():
                if command[chat_id] == '/find':
                    nfile = int(command_input) - 1
                else:
                    nfile = 4
                if (int(key) <= nfile):
                    if (tipo[chat_id] == 'files'):
                        textMessage = ("📦 [" + json_data[key]['name'] + "](" +
                                    json_data[key]['url'] + ")\n\n⬇️ `(" + json_data[key]['ndownload'] + ")`" + "\nℹ️ *" + json_data[key]['size'] + "\n🗓️ " + json_data[key]['upload_date'] + "*")
                    if (tipo[chat_id] == 'devices'):
                        textMessage = ("📲 [" + json_data[key]['name'] + "](" +
                                    json_data[key]['url'] + ")\n\n📱 `(" + json_data[key]['codename'] + ")`")
                    if (tipo[chat_id] == 'developers'):
                        textMessage = ("👤 [" + json_data[key]['name'] + "](" +
                                    json_data[key]['url'] + ")")
                    bot.sendMessage(chat_id, textMessage,
                                        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        except:
            bot.sendMessage(
                        chat_id, "*Nessun file trovato. Prova command cercare qualcosa di più specifico*", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        user_state[chat_id] = 0


def register_user(chat_id):
    """
    Register given user to receive news
    """
    insert = 1

    try:
        f = open(client_file, "r+")

        for user in f.readlines():
            if user.replace('\n', '') == str(chat_id):
                insert = 0

    except IOError:
        f = open(client_file, "w")

    if insert:
        f.write(str(chat_id) + '\n')

    f.close()

    return insert


# Main
print("Avvio AFHSearchBot")

# PID file
pid = str(os.getpid())
pidfile = "/tmp/AFHSearchBot.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Start working
try:
    bot = telepot.Bot(token)
    bot.message_loop(on_chat_message)
    while 1:
        sleep(10)

finally:
    os.unlink(pidfile)
