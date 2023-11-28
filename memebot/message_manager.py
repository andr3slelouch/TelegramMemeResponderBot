import logging
from telegram import Update, Message
from telegram.ext import ContextTypes, CallbackContext

from meme_manager import MemeManager
from config import config
from config.config import get_video_location
from utils.utils import string_normalizer, prepare_words

logger = logging.getLogger(__name__)


class MessageManager:
    def __init__(self):
        self.meme = MemeManager()

    async def answer_meme(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # TODO Implement answering/sending messages to topics
        # TODO Implement specifying allowed topic to answer
        meme = self.meme.get_meme_sticker(string_normalizer(update.message.text))
        if meme:
            await self._process_meme(meme, update, context)
        else:
            await self._answer_to_insult(update, context)

    async def _answer_to_insult(self, update, context):
        normalized_text = string_normalizer(update.message.text)
        insults = [
            "pinche bot", "bot culiao", "bot cdlbv",
            "bot conchatumadre", "bot crvrg"
        ]
        if normalized_text in insults:
            await self._random_meme(update, context)

    async def _random_meme(self, update, context):
        sticker_to_send = self.meme.random_stickers(1)[0]
        await self._send_sticker_or_video(sticker_to_send, update, context)

    async def _send_sticker_or_video(self, sticker, update, context):
        if "|" not in sticker:
            if "video" in sticker:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=open(get_video_location(sticker.split(":")[1]), "rb")
                )
            else:
                await context.bot.send_sticker(
                    chat_id=update.effective_chat.id,
                    sticker=sticker,
                )
        else:
            stickers_to_send = prepare_words(sticker)
            for sticker in stickers_to_send:
                if "video" in sticker:
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=open(get_video_location(sticker.split(":")[1]), "rb")
                    )
                if "time" not in sticker:
                    await context.bot.send_sticker(
                        chat_id=update.effective_chat.id,
                        sticker=sticker,
                    )

    async def _process_meme(self, meme, update, context):
        if type(meme) is not list:
            await self._answer_solo_sticker(meme, update)
        elif type(meme) is list:
            await self._answer_to_list_stickers(meme, update, context)

    async def _answer_to_list_stickers(self, meme, update, context):
        message = self._get_message_from_update(update)
        if "video" in meme[0]:
            await message.reply_video(open(get_video_location(meme[0].split(":")[1]), "rb"))
            await self._schedule_video_message(context, message, meme[1])
        else:
            for sticker in meme:
                await update.message.reply_sticker(sticker)

    async def _schedule_video_message(self, context, message, time_phrase):
        # TODO Finalize implementation
        meme = []
        if time_phrase is not None and "time" in time_phrase:
            seconds_to_add = int(time_phrase.split(":")[1]) * 60
            await context.job_queue.run_once(
                self._callback_video_message,
                seconds_to_add,
                context=(message.chat.id, get_video_location(meme[0].split(":")[1]), message.message_id),
            )

    def _get_message_from_update(self, update):
        return update.message.reply_to_message if update.message.reply_to_message is not None else update.message

    async def _callback_video_message(self, context):
        (chat_id, video_path, message_id) = context.job.context
        try:
            context.bot.send_video(
                chat_id=chat_id, video=open(video_path, "rb"), reply_to_message_id=message_id
            )
        except Exception as e:
            logger.warning("cannot reply message {}: {}".format(message_id, e))

    async def _answer_solo_sticker(self, meme, update):
        message = self._get_message_from_update(update)
        if "video" in meme:
            await message.reply_video(open(get_video_location(meme.split(":")[1]), "rb"))
        else:
            await message.reply_sticker(meme)

    async def answer_to_insult(self, update, context):
        if (
                string_normalizer(update.message.text) == "pinche bot"
                or string_normalizer(update.message.text) == "bot culiao"
                or string_normalizer(update.message.text) == "bot cdlbv"
                or string_normalizer(update.message.text) == "bot conchatumadre"
                or string_normalizer(update.message.text) == "bot crvrg"
        ):
            await self.random_meme(update, context)

    async def random_meme(self, update: Update, context: CallbackContext) -> None:
        """Send a random sticker"""
        sticker_to_send = self.meme.random_stickers(1)
        if "|" not in sticker_to_send[0]:
            if "video" in sticker_to_send[0]:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=open(config.get_video_location(sticker_to_send[0].split(":")[1]), "rb")
                )
            else:
                await context.bot.send_sticker(
                    chat_id=update.effective_chat.id,
                    sticker=sticker_to_send[0],
                )
        else:
            stickers_to_send = prepare_words(sticker_to_send[0])
            for sticker in stickers_to_send:
                if "video" in sticker:
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=open(config.get_video_location(sticker.split(":")[1]), "rb")
                    )
                if "time" not in sticker:
                    await context.bot.send_sticker(
                        chat_id=update.effective_chat.id,
                        sticker=sticker,
                    )
