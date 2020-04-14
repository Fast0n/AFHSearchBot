import logging
import json
import requests

import telegram.error as tg_error
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import (ParseMode, MessageEntity, ChatAction,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater, ConversationHandler)

from settings import token, start_msg, typepad, type_, url_api


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

NAME, ELEMENTSEARCH, RESULT = range(3)


def markup_key():

    arr = []
    for i in (range(0, len(list(range(1, 16))))):
        arr.append(str(list(range(1, 16))[i]))

    arrs = []
    while len(arr) > 4:
        pice = arr[:4]
        arrs.append(pice)
        arr = arr[4:]
    arrs.append(arr)

    return arrs


reply_keyboard = markup_key()


def start(update, context):
    """Send starting message"""
    update.message.reply_text(start_msg,  parse_mode=ParseMode.MARKDOWN)


def find(update, context):
    context.user_data['search_type'] = update.message.text
    update.message.reply_text("Cosa stai cercando?",  parse_mode=ParseMode.MARKDOWN,
                              reply_markup=ReplyKeyboardMarkup(typepad, one_time_keyboard=True, resize_keyboard=True))

    return NAME


def name(update, context):
    context.user_data['type'] = update.message.text
    update.message.reply_text(
        "Nome " + type_[update.message.text], reply_markup=ReplyKeyboardRemove())

    if context.user_data['search_type'] == "/find":
        update.message.reply_text("Quanti file vuoi visualizzare? (Solo numeri)",  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return ELEMENTSEARCH

    elif context.user_data['search_type'] == "/direct":
        context.user_data['elementseach'] = update.message.text
        return RESULT


def elementsearch(update, context):
    context.user_data['elementseach'] = update.message.text

    return RESULT


def result(update, context):

    link = "https://www.androidfilehost.com/?w=search&s=" + context.user_data['elementseach'].lower().replace(" ", "-") + \
        "&type=" + context.user_data['type']
    URL = url_api + "?search=" + \
        context.user_data['elementseach'].replace(
            ' ', '%20') + "&type=" + context.user_data['type']

    r = requests.get(URL, allow_redirects=True)

    try:
        json_data = json.loads(r.text)
        update.message.reply_text("Ho cercando: \n`" +
                                  link + "`", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(
                                      [[InlineKeyboardButton(text="Scopri di più",
                                                             url=link)]]))

        for key in json_data.keys():
            if context.user_data['search_type'] == '/find':
                nfile = int(update.message.text) - 1
            else:
                nfile = 4
            if (int(key) <= nfile):
                if (context.user_data['type'] == 'files'):
                    textMessage = ("📦 [" + json_data[key]['name'] + "](" +
                                   json_data[key]['url'] + ")\n\n⬇️ `(" + json_data[key]['ndownload'] + ")`" + "\nℹ️ *" + json_data[key]['size'] + "\n🗓️ " + json_data[key]['upload_date'] + "*")
                if (context.user_data['type'] == 'devices'):
                    textMessage = ("📲 [" + json_data[key]['name'] + "](" +
                                   json_data[key]['url'] + ")\n\n📱 `(" + json_data[key]['codename'] + ")`")
                if (context.user_data['type'] == 'developers'):
                    textMessage = ("👤 [" + json_data[key]['name'] + "](" +
                                   json_data[key]['url'] + ")")
                update.message.reply_text(textMessage,
                                          parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        print(e)
        update.message.reply_text("*Nessun file trovato. Prova command cercare qualcosa di più specifico*",
                                  parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def dona(update, context):
    update.message.reply_text("Codice sorgente: \n" +
                              "[AFHSearchBot](https://github.com/Fast0n/AFHSearchBot)\n\n" +
                              "Sviluppato da: \n" +
                              "[Fast0n](https://github.com/Fast0n)\n\n" +
                              "🍺 Se sei soddisfatto offrimi una birra 🍺", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(
                                  [[InlineKeyboardButton(text="Dona",
                                                         url="https://paypal.me/Fast0n/")]]))
    return ConversationHandler.END


def error(update, context):
    """Log errors caused by updates"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Starts the bot"""
    print("Avvio AFHSearchBot")

    # Create the Updater
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & (~Filters.regex(
            '^(/start)$') & (~Filters.regex('^(/dona)$')) & (~Filters.regex('^(/direct)$') & (~Filters.regex('^(/find)$')))), find)],

        states={

            NAME: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), name)],
            ELEMENTSEARCH: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), elementsearch)],
            RESULT: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), result)],

        },

        fallbacks=[MessageHandler(Filters.text & (
            Filters.regex('^(Stop)$')), start)]

    )

    # Register handlers
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("find", find))
    dp.add_handler(CommandHandler("direct", find))
    dp.add_handler(CommandHandler("dona", dona))

    # Register error handler
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
