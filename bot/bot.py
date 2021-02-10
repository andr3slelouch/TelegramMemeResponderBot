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
    if hasattr(update.message, "date"):
        if update.message.date > START_BOT_DATETIME:
            meme = get_meme_sticker(string_normalizer(update.message.text))
            if meme:
                update.message.reply_sticker(meme)
            else:
                meme = get_meme_url(string_normalizer(update.message.text))
                if meme:
                    update.message.reply_photo(meme)


def get_sticker_id(update: Update, context: CallbackContext) -> None:
    sticker_id = update.message.sticker.file_id
    id = str(update.message.from_user["id"])
    chat_id = str(update.message.chat.id)
    if sticker_id and id == str(232424901) and chat_id == str(232424901):
        context.bot.send_message(chat_id=232424901, text=str(sticker_id))


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
    message = get_meme_list_summary()
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
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        meme_df = df.loc[df["Meme"] == meme]
        return meme_df.iloc[0, 1]
    except:
        return False


def get_meme_sticker(meme: str) -> str:
    try:
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        meme_df = df.loc[df["Meme"] == meme]
        return meme_df.iloc[0, 2]
    except:
        return False


def get_sticker_list() -> [str]:
    try:
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        list_of_memes = df["StickerID"].tolist()
        return list_of_memes
    except:
        return False


def get_meme_list() -> [str]:
    try:
        df = pd.read_excel("/home/pi/Projects/memeBot/data/meme_bot_db.xlsx")
        list_of_memes = df["Meme"].tolist()
        return list_of_memes
    except:
        return False


def get_meme_list_dict() -> dict:
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


def get_meme_list_summary() -> str:
    list_of_memes = get_meme_list()
    counter = 0
    summary = ""
    if list_of_memes:
        for meme in list_of_memes:
            counter += 1
            summary += str(counter) + ". " + meme + "\n"
        return summary
    else:
        return False


def random_stickers(n: int) -> [str]:
    ids = get_sticker_list()
    random.shuffle(ids)
    return ids[:n]


def into_words(q: str) -> [str]:
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
    for w in words:
        if w.startswith(word):
            return True
    return False


def search_stickers(query: str) -> [str]:
    query_words = into_words(query)
    dict_stickers = get_meme_list_dict()

    stickers = []
    for file_id, texts in dict_stickers.items():
        texts_string = " ".join(texts).lower()
        texts_words = into_words(texts_string)
        if all([word_in_words(w, texts_words) for w in query_words]):
            stickers.append(file_id)

    return stickers


def on_query(update: Update, context: CallbackContext):
    # This constant is defined by the Bot API.
    MAX_RESULTS = 50

    inline_query = update.inline_query
    query = inline_query.query
    offset = update.inline_query.offset

    if not inline_query:
        return

    # If query is empty - return random stickers.
    return_random = not inline_query.query

    if return_random:
        stickers = random_stickers(MAX_RESULTS)
    else:
        stickers = search_stickers(inline_query.query)

    if len(stickers) > MAX_RESULTS:
        stickers = stickers[:MAX_RESULTS]

    """ results = [
        InlineQueryResultCachedSticker(id=uuid4(), sticker_file_id=fid)
        for fid in stickers
    ] """

    """ cache_time = 600
    if return_random:
        # Do not cache random results.
        cache_time = 0 """
    """     results = list()
    results.append(
        InlineQueryResultCachedSticker(
            id=uuid4(), sticker_file_id="BQADBAADXwADAtezAg6Zqq6f1-PwAg"
        )
    ) """
    results: typing.List[InlineQueryResultCachedSticker] = []
    print(stickers[0] + "\n")
    for sticker_file_id in stickers:
        results.append(
            InlineQueryResultCachedSticker(
                id=uuid4(),
                sticker_file_id=sticker_file_id,
                input_message_content=InputTextMessageContent(
                    f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
                ),
            ),
        )

    update.inline_query.answer(inline_query.id, results)


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query
    """ results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultCachedSticker(
            id=uuid4(),
            title="Ejemplo",
            sticker_file_id="BQADBAADXwADAtezAg6Zqq6f1-PwAg",
        ),
    ] """

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
    else:
        stickers = search_stickers(inline_query.query)

    if len(stickers) > MAX_RESULTS:
        stickers = stickers[:MAX_RESULTS]

    for sticker_file_id in stickers:
        results.append(
            InlineQueryResultCachedSticker(
                id=uuid4(),
                sticker_file_id=sticker_file_id,
            ),
        )

    update.inline_query.answer(results)


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

    # add inlinequery
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.sticker, get_sticker_id))
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