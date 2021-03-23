#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
This code is based in Simple Bot to reply to Telegram messages example located
in https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py.

"""

import logging
import configuration
import image_converter
import os

from telegram import (
    Update,
    ParseMode,
    Bot,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
    InlineQueryResultArticle,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    InlineQueryHandler,
)
from telegram.utils.helpers import escape_markdown
from datetime import datetime, timezone
import re
from unicodedata import normalize
import pandas as pd
import traceback
import html
import json
import random
from uuid import uuid4
import typing
import time
from collections import OrderedDict

START_BOT_DATETIME = datetime.now(timezone.utc)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def word_count(string):
    # Here we are removing the spaces from start and end,
    # and breaking every word whenever we encounter a space
    # and storing them in a list. The len of the list is the
    # total count of words.
    return len(string.strip().split(" "))


def prepare_words(string) -> list:
    """This function prepare a string that has | in his content and split in a list

    Args:
        string (str): Wort to be splitted

    Returns:
        list: A list that contains the string splitted in a list
    """
    list_words = string.strip().split("|")
    return [word.strip() for word in list_words]


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    if hasattr(update.message, "date"):
        if update.message.date > START_BOT_DATETIME:
            meme = get_meme_sticker(string_normalizer(update.message.text))
            if meme and type(meme) is not list:
                update.message.reply_sticker(meme)
            elif type(meme) is list:
                for sticker in meme:
                    update.message.reply_sticker(sticker)


def get_sticker_id(update: Update, context: CallbackContext) -> None:
    """This funtion returns the id of the sticker and send it to the admin user"""
    sticker_id = update.message.sticker.file_id
    id = str(update.message.from_user["id"])
    chat_id = str(update.message.chat.id)
    if sticker_id and id == str(232424901) and chat_id == str(232424901):
        context.bot.send_message(chat_id=232424901, text=str(sticker_id))


def id(update: Update, context: CallbackContext) -> None:
    """Answer the id user"""
    id = update.message.from_user["id"]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=str(id),
    )


# Taken from https://github.com/Koppal-Shree/telegram_gcloner/blob/4eda6ed55fbabae47c59aa81decdb15dc1f211bb/telegram_gcloner/utils/callback.py
def callback_delete_message(context: CallbackContext):
    """This callback function allow to delete a message"""
    (chat_id, message_id) = context.job.context
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.warning("cannot delete message {}: {}".format(message_id, e))


def list_memes(update: Update, context: CallbackContext) -> None:
    """List all memes"""
    id = update.message.from_user["id"]
    message = get_meme_list_summary(0)
    if message:
        sended_msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        context.job_queue.run_once(
            callback_delete_message,
            30,
            context=(update.effective_chat.id, sended_msg.message_id),
        )


def top_memes(update: Update, context: CallbackContext) -> None:
    """List Top 10 last memes"""
    id = update.message.from_user["id"]
    message = get_meme_list_summary(-10)
    if message:
        sended_msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        context.job_queue.run_once(
            callback_delete_message,
            60,
            context=(update.effective_chat.id, sended_msg.message_id),
        )


def string_normalizer(phrase: str) -> str:
    """This functions is made for clean any character different to ascii

    Args:
        phrase (str): Phrase to be normalized

    Returns:
        str: Normalized string to be compared to memes in list
    """
    phrase = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+",
        r"\1",
        normalize("NFD", phrase),
        0,
        re.I,
    )
    # -> NFC
    phrase = normalize("NFC", phrase)
    phrase = phrase.replace(",", "")
    phrase = phrase.lower()
    return phrase


def get_meme_sticker(meme: str) -> str:
    """Find the sticker in excel and return its id

    Args:
        meme (str): Meme phrase to search

    Returns:
        str: Returns the id of the sticker to be sended
    """
    try:
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        for index, row in df.iterrows():
            list_words = prepare_words(row["Meme"])
            for submeme in list_words:
                if meme == submeme:
                    if not "|" in row["StickerID"]:
                        return row["StickerID"]
                    else:
                        return prepare_words(row["StickerID"])
    except:
        return False


def get_sticker_list() -> [str]:
    """Makes a list from all thestickers in excel

    Returns:
        [str]: List of stickers
    """
    try:
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        list_of_memes = df["StickerID"].tolist()
        return list_of_memes
    except:
        return False


def get_meme_list() -> [str]:
    """Makes a list from all the memes in excel

    Returns:
        [str]: List of memes
    """
    try:
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        shortened_df = df.tail(137)
        list_of_memes = shortened_df["Meme"].tolist()
        return list_of_memes
    except:
        return False


def get_meme_list_dict() -> dict:
    """Makes a dict with all the memes and stickers."""
    try:
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        list_of_memes = df["Meme"].tolist()
        list_of_stickers = df["StickerID"].tolist()
        stickers_dict = {}
        for sticker, meme in zip(list_of_stickers, list_of_memes):
            stickers_dict.update({sticker: [meme]})
        return stickers_dict
    except:
        return False


def get_meme_list_summary(elements_from_last: int) -> str:
    """Prepares the a list of the last memes to be sended as string

    Args:
        elements_from_last (int): How much elements are required

    Returns:
        str: The summary of memes
    """
    list_of_memes = get_meme_list()
    counter = 0
    summary = ""
    if list_of_memes:
        for meme in list_of_memes[elements_from_last:]:
            counter += 1
            if "|" in str(meme):
                splited_meme = meme.split("|")
                variante_word = "variante"
                if len(splited_meme) > 1:
                    variante_word += "s"
                meme = (
                    str(splited_meme[0]).strip()
                    + " ("
                    + str(len(splited_meme))
                    + " "
                    + variante_word
                    + ")"
                )
            summary += str(counter) + ". " + str(meme) + "\n"
        return summary
    else:
        return False


def random_stickers(n: int) -> [str]:
    """Returns a random list of stickers

    Args:
        n (int): How much memes are required

    Returns:
        [str]: The list of the required stickers
    """
    ids = get_sticker_list()
    random.shuffle(ids)
    for meme in ids:
        if "|" in meme:
            ids.remove(meme)
            for substicker in meme.split("|"):
                ids.append(substicker.strip())
    return list(OrderedDict.fromkeys(ids[:n]))


def random_meme(update: Update, context: CallbackContext) -> None:
    """Send a random sticker"""
    id = update.message.from_user["id"]
    sticker_to_send = random_stickers(1)
    if not "|" in sticker_to_send[0]:
        sended_msg = context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker=sticker_to_send[0],
        )
    else:
        stickers_to_send = prepare_words(sticker_to_send[0])
        for sticker in sticker_to_send:
            sended_msg = context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=sticker,
            )


def into_words(q: str) -> [str]:
    """This function split a string to his characters

    Args:
        q (str): String to be splitted

    Returns:
        [str]: List of characters
    """
    # Remove all syntax symbols
    syntax_marks = ",.!?-"
    for sym in syntax_marks:
        q = q.replace(sym, " ")

    # Split into words
    words = q.lower().strip().split()
    words = [w.strip() for w in words]
    words = [w for w in words if w]

    return words


def word_in_words(word: str, words: [str]) -> bool:
    """Returns if a word exists inside the list of words

    Args:
        word (str): Word to be finded
        words ([str]): List of words

    Returns:
        bool: Returns True if the word is found else False
    """
    for w in words:
        if w.startswith(word):
            return True
    return False


def search_stickers(query: str) -> [str]:
    """This function finds a meme andreturns his repective stickers

    Args:
        query (str): Meme to be found

    Returns:
        [str]: List of stickers ids to be used in inlinequery
    """
    query_words = into_words(query)
    dict_stickers = get_meme_list_dict()

    stickers = []
    for file_id, texts in dict_stickers.items():
        texts_string = " ".join(texts).lower()
        texts_words = into_words(texts_string)
        if "*" in texts:
            continue
        if all([word_in_words(w, texts_words) for w in query_words]):
            if "|" in file_id:
                for sticker in prepare_words(file_id):
                    stickers.append(sticker)
            else:
                stickers.append(file_id)

    return list(OrderedDict.fromkeys(stickers))


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    results = []

    # This constant is defined by the Bot API.
    MAX_RESULTS = 50

    inline_query = update.inline_query
    query = update.inline_query.query
    offset = update.inline_query.offset

    if not inline_query:
        return

    # If query is empty - return random stickers.
    return_random = not inline_query.query

    if return_random:
        stickers = random_stickers(MAX_RESULTS)
    elif query == "":
        stickers = random_stickers(MAX_RESULTS)
    else:
        stickers = search_stickers(inline_query.query)

    stickers = list(dict.fromkeys(stickers))

    if len(stickers) > MAX_RESULTS:
        stickers = stickers[:MAX_RESULTS]

    for sticker_file_id in stickers:
        results.append(
            InlineQueryResultCachedSticker(
                id=uuid4(),
                sticker_file_id=sticker_file_id,
            ),
        )
    if len(results) > 0:
        update.inline_query.answer(results)


def answer_webp(update: Update, context: CallbackContext) -> None:
    try:
        id = str(update.message.from_user["id"])
    except:
        id = ""
    chat_id = str(update.message.chat.id)
    if (
        len(update.message.photo) > 0
        and id == str(232424901)
        and chat_id == str(232424901)
    ):
        photo = update.message.photo[-1]
        newFile = photo.get_file()
        temp_file_path = newFile.file_path
        extw = temp_file_path.split("/")
        fname = extw[len(extw) - 1]
        newFile.download(fname)
        sticker_fname = image_converter.convert_image(fname, "jpg")
        update.message.reply_sticker(open(sticker_fname, "rb"))
        os.remove(fname)
        os.remove(sticker_fname)


def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    context.bot.send_message(chat_id=232424901, text=message, parse_mode=ParseMode.HTML)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        token=configuration.get_bot_token(
            configuration.get_file_location("config.yaml")
        ),
    )

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("id", id))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("list", list_memes))
    dispatcher.add_handler(CommandHandler("top", top_memes))
    dispatcher.add_handler(CommandHandler("random", random_meme))

    # add inlinequery
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.sticker, get_sticker_id))
    dispatcher.add_handler(MessageHandler(Filters.photo, answer_webp))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()