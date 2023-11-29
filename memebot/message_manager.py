import logging
from telegram import Update, Message
from telegram.ext import ContextTypes, CallbackContext

from memebot.meme_manager import MemeManager
from config import config
from config.config import get_video_location
from utils.utils import string_normalizer, prepare_words, process_video_parameters_to_dict

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

    async def verify_all_meme(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        for index, row in self.meme.meme_database_df.iterrows():
            await update.message.reply_text(f"Testing {row['Meme']}")
            await self._send_sticker_or_video(row['StickerID'], update, context)

    async def list_memes(self, update: Update, context: CallbackContext) -> None:
        """List all memes"""
        messages_list = self.meme.get_meme_list_summary()
        if messages_list:
            for message in messages_list:
                sent_msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                )
                context.job_queue.run_once(
                    self._callback_delete_message,
                    30,
                    data=(update.effective_chat.id, sent_msg.message_id),
                )

    async def _answer_to_insult(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        normalized_text = string_normalizer(update.message.text)
        insults = [
            "pinche bot", "bot culiao", "bot cdlbv",
            "bot conchatumadre", "bot crvrg"
        ]
        if normalized_text in insults:
            await self.random_meme(update, context)

    async def random_meme(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        This method selects a random meme to send
        :param update: Update of the current session
        :param context: Context of the current session
        :return: None
        """
        sticker_to_send = self.meme.random_stickers(1)[0]
        await self._send_sticker_or_video(sticker_to_send, update, context)

    async def _send_sticker_or_video(self, sticker: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        This method decides how to send a sticker or a video to the chat
        :param sticker: Sticker ID to send
        :param update: Telegram Update of the session
        :param context: Telegram Context of the session
        :return: None
        """

        async def send_single_sticker(sticker_id_str: str):
            if "video" in sticker_id_str:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=open(get_video_location(sticker_id_str.split(":")[1]), "rb"),
                    reply_to_message_id= update.message.message_id
                )
            else:
                await context.bot.send_sticker(
                    chat_id=update.effective_chat.id,
                    sticker=sticker_id_str,
                    reply_to_message_id=update.message.message_id
                )

        if "|" not in sticker:
            await send_single_sticker(sticker)
        else:
            stickers_to_send = prepare_words(sticker)
            for sticker_id in stickers_to_send:
                if "time" not in sticker_id:
                    await send_single_sticker(sticker_id)

    async def _process_meme(self, meme, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if type(meme) is not list:
            await self._answer_solo_sticker(meme, update)
        elif type(meme) is list:
            await self._answer_to_list_stickers(meme, update, context)

    async def _answer_to_list_stickers(self, meme, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = self._get_message_from_update(update)
        if "video" in meme[0]:
            await message.reply_video(open(get_video_location(meme[0].split(":")[1]), "rb"))
            await self._schedule_video_message(context, message, meme)
        else:
            for sticker in meme:
                await update.message.reply_sticker(sticker)

    async def _schedule_video_message(self, context: ContextTypes.DEFAULT_TYPE, message: Message, time_phrase: [str]):
        video_parameters = process_video_parameters_to_dict(time_phrase)
        video_path = get_video_location(video_parameters.get("video", ""))
        if video_parameters.get("time", None) is not None:
            seconds_to_add = int(video_parameters.get("time", 0))
            if video_parameters.get("accuracy","") != "s":
                seconds_to_add *= 60
            logger.info(f"Seconds to add {seconds_to_add}")
            context.job_queue.run_once(
                self._callback_video_message,
                seconds_to_add,
                chat_id=message.chat_id,
                data=(
                    message.chat.id,
                    video_path,
                    message.message_id
                )
            )

    def _get_message_from_update(self, update: Update):
        return update.message.reply_to_message if update.message.reply_to_message is not None else update.message

    async def _callback_video_message(self, context):
        (chat_id, video_path, message_id) = context.job.data
        logger.info(
            f"Executing callback_video_message chat_id {chat_id}, video_path {video_path}, message_id {message_id}")
        try:
            await context.bot.send_video(
                chat_id=chat_id, video=open(video_path, "rb"), reply_to_message_id=message_id
            )
        except Exception as e:
            logger.warning("cannot reply message {}: {}".format(message_id, e))

    async def _callback_delete_message(self, context):
        """This callback function allow to delete a message"""
        (chat_id, message_id) = context.job.data
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.warning("cannot delete message {}: {}".format(message_id, e))

    async def _answer_solo_sticker(self, meme, update: Update):
        message = self._get_message_from_update(update)
        if "video" in meme:
            await message.reply_video(open(get_video_location(meme.split(":")[1]), "rb"))
        else:
            await message.reply_sticker(meme)

    async def answer_to_insult(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (
                string_normalizer(update.message.text) == "pinche bot"
                or string_normalizer(update.message.text) == "bot culiao"
                or string_normalizer(update.message.text) == "bot cdlbv"
                or string_normalizer(update.message.text) == "bot conchatumadre"
                or string_normalizer(update.message.text) == "bot crvrg"
        ):
            await self.random_meme(update, context)
