import logging
from uuid import uuid4

from telegram import Update, InlineQueryResultCachedSticker
from telegram.ext import ContextTypes

from memebot.meme_manager import MemeManager

logger = logging.getLogger(__name__)

class InlineKeyboardManager:

    def __init__(self):
        self.meme = MemeManager()

    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the inline query."""

        results = []

        # This constant is defined by the Bot API.
        max_results = 50

        inline_query_str = update.inline_query
        query = update.inline_query.query
        logger.info(f"QUERY to inline {query}")
        if not inline_query_str:
            return

        # If query is empty - return random stickers.
        return_random = not inline_query_str.query

        # TODO Fix sending random stickers

        if return_random:
            # stickers = self.meme.random_stickers(max_results)
            stickers = self.meme.search_stickers("?")
        elif query == "":
            # stickers = self.meme.random_stickers(max_results)
            stickers = self.meme.search_stickers("?")
        else:
            stickers = self.meme.search_stickers(inline_query_str.query)

        stickers = list(dict.fromkeys(stickers))

        if len(stickers) > max_results:
            stickers = stickers[:max_results]

        for sticker_file_id in stickers:
            if sticker_file_id:
                results.append(
                    InlineQueryResultCachedSticker(
                        id=str(uuid4()),
                        sticker_file_id=sticker_file_id,
                    ),
                )
        if len(results) > 0:
            await update.inline_query.answer(results)
