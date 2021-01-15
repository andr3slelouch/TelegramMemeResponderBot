#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from datetime import datetime, timezone
import re
from unicodedata import normalize
import pandas as pd
import traceback
import html
import json

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


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    if update.message.date > START_BOT_DATETIME:
        meme_url = get_meme_url(string_normalizer(update.message.text))
        # update.message.reply_text(update.message.text)
        if meme_url:
            update.message.reply_photo(meme_url)


def id(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    id = update.message.from_user["id"]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=str(id),
    )


def list_memes(update: Update, context: CallbackContext) -> None:
    """List all memes"""
    id = update.message.from_user["id"]
    message = get_meme_list()
    if message:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )


def string_normalizer(phrase: str) -> str:
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


def get_meme_url(meme: str) -> str:
    try:
        df = pd.read_excel("data/meme_bot_db.xlsx")
        meme_df = df.loc[df["Meme"] == meme]
        return meme_df.iloc[0, 1]
    except:
        return False


def get_meme_list() -> str:
    try:
        df = pd.read_excel("data/meme_bot_db.xlsx")
        list_of_memes = df["Meme"].tolist()
        counter = 0
        summary = ""
        for meme in list_of_memes:
            counter += 1
            summary += str(counter) + ". " + meme + "\n"
        return summary
    except:
        return False


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
        "1515669604:AAHH4PLj_dF6w01Ke16DJ30w04aCHEImxwk", use_context=True
    )

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("id", id))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("list", list_memes))

    # on noncommand i.e message - echo the message on Telegram
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