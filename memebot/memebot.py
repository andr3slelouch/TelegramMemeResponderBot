#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import html
import json
import logging
import traceback

from telegram import ForceReply, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, \
    InlineQueryHandler

from config.config import load_config
from memebot.inline_keyboard_manager import InlineKeyboardManager
from memebot.message_manager import MessageManager

message_man = MessageManager()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await message_man.verify_all_meme(update, context)


async def list_memes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await message_man.list_memes(update, context)


async def random_meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await message_man.random_meme(update, context)


async def prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await message_man.prompt_reply(update, context)

async def answer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await message_man.prompt_reply(update, context)


async def answer_meme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Method to answer a meme"""
    await message_man.answer_meme(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""

    # Log the error before we do anything else, so we can see it even if something breaks.

    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a

    # list of strings rather than a single string, so we have to join them together.

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)

    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.

    # You might need to add some logic to deal with messages longer than the 4096-character limit.

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    message = (

        "An exception was raised while handling an update\n"

        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"

        "</pre>\n\n"

        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"

        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"

        f"<pre>{html.escape(tb_string)}</pre>"

    )

    # Finally, send the message
    config_data = load_config()
    chat_id = config_data.get("telegram_api", {}).get("error_handler_message_id", "")

    await context.bot.send_message(

        chat_id=chat_id, text=message, parse_mode=ParseMode.HTML

    )


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    config_data = load_config()
    api_key = config_data.get("telegram_api", {}).get("api_key", "")
    application = Application.builder().token(api_key).build()

    inline_query = InlineKeyboardManager()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("verify", verify_command))
    application.add_handler(CommandHandler("list", list_memes_command))
    application.add_handler(CommandHandler("random", random_meme_command))
    application.add_handler(CommandHandler("prompt", prompt_command))
    application.add_handler(CommandHandler("answer", prompt_command))
    application.add_handler(InlineQueryHandler(inline_query.inline_query))

    # on non command i.e. message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_meme))

    application.add_error_handler(error_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
