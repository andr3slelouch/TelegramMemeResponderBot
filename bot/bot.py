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
from typing import Any
import configuration
import image_converter
import video_converter
import os

from telegram import (
    Update,
    ParseMode,
    Bot,
    InlineQueryResultCachedSticker,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    InlineQueryHandler,
)
from datetime import datetime, timezone
from unicodedata import normalize
import pandas as pd
import traceback
import html
import json
import random
from uuid import uuid4
from collections import OrderedDict
import csv
import re

OUTPUT_STICKER_WEBM = "output_sticker.webm"

JO_JO_POSES_XLSX = "/home/pi/Projects/memeBot/data/JoJo_Poses.xlsx"

MEME_BOT_DB_XLSX = "/home/pi/Projects/memeBot/data/meme_bot_db.xlsx"

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


def greet_new_chat_members(update: Update, context: CallbackContext):
    bot = Bot(token=configuration.get_bot_token(
        configuration.get_file_location("config.yaml")
    ))
    sent_msg = bot.send_animation(update.effective_chat.id, "https://media.giphy.com/media/Vste8Y15c34zK/giphy.gif")
    context.job_queue.run_once(
        callback_delete_message,
        30,
        context=(update.effective_chat.id, sent_msg.message_id),
    )


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
            elif (
                    string_normalizer(update.message.text) == "pinche bot"
                    or string_normalizer(update.message.text) == "bot culiao"
                    or string_normalizer(update.message.text) == "bot cdlbv"
                    or string_normalizer(update.message.text) == "bot conchatumadre"
                    or string_normalizer(update.message.text) == "bot crvrg"
            ):
                random_meme(update, context)


def get_sticker_id(update: Update, context: CallbackContext) -> None:
    """This funtion returns the id of the sticker and send it to the admin user"""
    sticker_id = update.message.sticker.file_id
    id = str(update.message.from_user["id"])
    chat_id = str(update.message.chat.id)
    if sticker_id and id == str(232424901) and chat_id == str(232424901):
        context.bot.send_message(chat_id=232424901, text=str(sticker_id))


def get_id(update: Update, context: CallbackContext) -> None:
    """Answer the id user"""
    user_id = update.message.from_user["id"]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=str(user_id),
    )


# Taken from https://github.com/Koppal-Shree/telegram_gcloner/blob/4eda6ed55fbabae47c59aa81decdb15dc1f211bb
# /telegram_gcloner/utils/callback.py
def callback_delete_message(context: CallbackContext):
    """This callback function allow to delete a message"""
    (chat_id, message_id) = context.job.context
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.warning("cannot delete message {}: {}".format(message_id, e))


def list_memes(update: Update, context: CallbackContext) -> None:
    """List all memes"""
    message = get_meme_list_summary(-100)
    if message:
        sent_msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        context.job_queue.run_once(
            callback_delete_message,
            30,
            context=(update.effective_chat.id, sent_msg.message_id),
        )


def ban_handler(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.type != "private":
        member_status = context.bot.get_chat_member(update.effective_chat.id, update.message.from_user["id"]).status
        if member_status == "creator" or member_status == "administrator":
            if update.message.reply_to_message is not None:
                add_banned_users_csv(update.effective_chat.id, str(update.message.reply_to_message.from_user["id"]))
            if update.message.entities is not None:
                for entity in update.message.entities:
                    if entity.type.find("text_mention") != -1:
                        print(entity.to_dict())
                        add_banned_users_csv(update.effective_chat.id, entity.user.id)
            if len(update.message.text.split(" ")) > 0:
                list_ids = update.message.text.split(" ")
                for id_element in list_ids:
                    if re.search("^(\\+|-)?\\d+$", id_element):
                        if get_user_from_id(update, context, id_element) is not None:
                            add_banned_users_csv(update.effective_chat.id, id_element)
                    elif id_element[0] == "@":
                        add_banned_users_csv(update.effective_chat.id, id_element)


def unban_handler(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.type != "private":
        member_status = context.bot.get_chat_member(update.effective_chat.id, update.message.from_user["id"]).status
        if member_status == "creator" or member_status == "administrator":
            banned_users = read_banned_users_csv()
            if len(banned_users) == 2:
                if str(update.effective_chat.id) in banned_users[0]:
                    if update.message.reply_to_message is not None:
                        delete_banned_user_csv(update.effective_chat.id,
                                               str(update.message.reply_to_message.from_user["id"]))
                    if update.message.entities is not None:
                        for entity in update.message.entities:
                            if entity.type.find("text_mention") != -1:
                                delete_banned_user_csv(update.effective_chat.id, entity.user.id)
                    if len(update.message.text.split(" ")) > 0:
                        list_ids = update.message.text.split(" ")
                        for id_element in list_ids:
                            if re.search("^(\\+|-)?\\d+$", id_element):
                                if get_user_from_id(update, context, id_element) is not None:
                                    delete_banned_user_csv(update.effective_chat.id, id_element)
                            elif id_element[0] == "@":
                                delete_banned_user_csv(update.effective_chat.id, id_element)


def get_user_from_id(update: Update, context: CallbackContext, user_id: str):
    try:
        chat_member = context.bot.get_chat_member(update.effective_chat.id, int(user_id))
        return chat_member.user
    except Exception as e:
        print(e)
        return None


def read_banned_users_csv() -> list:
    # reading csv file
    # creating a csv reader object
    csvreader = csv.DictReader(open("/home/pi/Projects/memeBot/data/banned_users.csv", 'r'))
    groups = []
    users = []
    for col in csvreader:
        groups.append(col["group"])
        users.append(col["user"])
    return [groups, users]


def add_banned_users_csv(group_id: str, user_id: str) -> None:
    # reading csv file
    # creating a csv reader object
    list_banned_users = []
    banned_users = read_banned_users_csv()
    user_to_add = {"group": group_id, "user": user_id}
    for (group, user) in zip(banned_users[0], banned_users[1]):
        list_banned_users.append({"group": group, "user": user})
    if not user_to_add in list_banned_users:
        keys = list_banned_users[0].keys()
        with open('/home/pi/Projects/memeBot/data/banned_users.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(list_banned_users)


def delete_banned_user_csv(group_id: str, user_id: str) -> list:
    # reading csv file
    # creating a csv reader object
    csvreader = csv.DictReader(open("/home/pi/Projects/memeBot/data/banned_users.csv", 'r'))
    groups = []
    users = []
    for col in csvreader:
        groups.append(col["group"])
        users.append(col["user"])
    return [groups, users]


def top_memes(update: Update, context: CallbackContext) -> None:
    """List Top 10 last memes"""
    message = get_meme_list_summary(-10)
    if message:
        sent_msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        context.job_queue.run_once(
            callback_delete_message,
            60,
            context=(update.effective_chat.id, sent_msg.message_id),
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
        df = pd.read_excel(MEME_BOT_DB_XLSX)
        for index, row in df.iterrows():
            list_words = prepare_words(row["Meme"])
            for sub_meme in list_words:
                if meme == sub_meme:
                    if not "|" in row["StickerID"]:
                        return row["StickerID"]
                    else:
                        return prepare_words(row["StickerID"])
    except Exception as e:
        return False


def get_sticker_list() -> [str]:
    """Makes a list from all thestickers in excel

    Returns:
        [str]: List of stickers
    """
    try:
        df = pd.read_excel(MEME_BOT_DB_XLSX)
        list_of_memes = df["StickerID"].tolist()
        return list_of_memes
    except Exception as e:
        return False


def get_jojo_pose_list() -> [str]:
    """Makes a list from all jojo poses in excel file

    Returns:
        [str]: List of stickers
    """
    try:
        df = pd.read_excel(JO_JO_POSES_XLSX)
        list_of_memes = df["URL"].tolist()
        return list_of_memes
    except Exception as e:
        return False


def get_meme_list() -> [str]:
    """Makes a list from all the memes in Excel

    Returns:
        [str]: List of memes
    """
    try:
        df = pd.read_excel(MEME_BOT_DB_XLSX)
        shortened_df = df.tail(130)
        list_of_memes = shortened_df["Meme"].tolist()
        return list_of_memes
    except Exception as e:
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
    except Exception as e:
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


def random_pose(n: int) -> [str]:
    """Returns a random list of stickers

    Args:
        n (int): How much memes are required

    Returns:
        [str]: The list of the required stickers
    """
    urls = get_jojo_pose_list()
    random.shuffle(urls)
    list_to_return = list(OrderedDict.fromkeys(urls[:n]))
    return list_to_return


def random_meme(update: Update, context: CallbackContext) -> None:
    """Send a random sticker"""
    sticker_to_send = random_stickers(1)
    if not "|" in sticker_to_send[0]:
        context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker=sticker_to_send[0],
        )
    else:
        stickers_to_send = prepare_words(sticker_to_send[0])
        for sticker in stickers_to_send:
            context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=sticker,
            )


def jojo_pose(update: Update, context: CallbackContext) -> None:
    """Send a random sticker"""
    sticker_to_send = random_pose(1)
    print(sticker_to_send)
    context.bot.send_photo(chat_id=id, photo=sticker_to_send[0])


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
        user_id = str(update.message.from_user["id"])
    except Exception as e:
        user_id = ""
    chat_id = str(update.message.chat.id)
    if (
            len(update.message.photo) > 0
            and user_id == str(232424901)
            and chat_id == str(232424901)
    ):
        photo = update.message.photo[-1]
        new_file = photo.get_file()
        temp_file_path = new_file.file_path
        ext = temp_file_path.split("/")
        name = ext[len(ext) - 1]
        new_file.download(name)
        sticker_name = image_converter.convert_image(name, "jpg")
        update.message.reply_sticker(open(sticker_name, "rb"))
        os.remove(name)
        os.remove(sticker_name)


def answer_webm(update: Update, context: CallbackContext) -> None:
    try:
        user_id = str(update.message.from_user["id"])
    except Exception as e:
        user_id = ""
    chat_id = str(update.message.chat.id)
    if (
            (update.message.video is not None or update.message.animation is not None)
            and user_id == str(232424901)
            and chat_id == str(232424901)
    ):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Processing video...",
        )
        new_file = None
        short_video = True
        if update.message.video is not None:
            new_file = update.message.video.get_file()
            print(update.message.video.duration)
            short_video = update.message.video.duration < 3
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Duration:" + update.message.video.duration + "Flag:" + str(short_video),
            )
        elif update.message.animation is not None:
            new_file = update.message.animation.get_file()
            print(update.message.animation.duration)
            short_video = update.message.animation.duration < 3
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Duration:" + str(update.message.animation.duration) + "Flag:" + str(short_video),
            )

        if new_file is not None:
            temp_file_path = new_file.file_path
            ext = temp_file_path.split("/")
            name = ext[len(ext) - 1]
            new_file.download(name)
            if video_converter.convert_video(name, not short_video) and os.path.exists(OUTPUT_STICKER_WEBM):
                update.message.reply_video(open(OUTPUT_STICKER_WEBM, "rb"))
                os.remove(name)
                os.remove(OUTPUT_STICKER_WEBM)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Something went wrong trying to convert video...",
                )


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
    dispatcher.add_handler(CommandHandler("pose", jojo_pose))
    dispatcher.add_handler(CommandHandler("ban", ban_handler))
    dispatcher.add_handler(CommandHandler("unban", unban_handler))

    # add inlinequery
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.sticker, get_sticker_id))
    dispatcher.add_handler(MessageHandler(Filters.photo, answer_webp))
    dispatcher.add_handler(MessageHandler(Filters.document.image, answer_webp))
    dispatcher.add_handler(MessageHandler(Filters.video, answer_webm))
    dispatcher.add_handler(MessageHandler(Filters.animation, answer_webm))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_new_chat_members))
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
