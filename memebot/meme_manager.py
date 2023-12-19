import random
import os
from collections import OrderedDict
from datetime import datetime
from typing import Any
import logging
import pandas as pd
from cysystemd.journal import JournaldLogHandler

from config.config import load_config, get_working_directory
from utils.utils import prepare_words, into_words, word_in_words

# get an instance of the logger object this module will use
logger = logging.getLogger(__name__)

# instantiate the JournaldLogHandler to hook into systemd
journald_handler = JournaldLogHandler()

# set a formatter to include the level name
journald_handler.setFormatter(logging.Formatter(
    '[%(levelname)s] %(message)s'
))

# add the journald handler to the current logger
logger.addHandler(journald_handler)

# optionally set the logging level
logger.setLevel(logging.DEBUG)

class MemeManager:
    meme_database_df = None

    def __init__(self):
        self.meme_database_df = None
        self.load_dataframe()

    def load_dataframe(self) -> None:
        if self.meme_database_df is None:
            config_data = load_config()
            meme_database_path = os.path.join(get_working_directory(),
                                              config_data.get("meme_managing", {}).get("meme_database", ""))
            self.meme_database_df = pd.read_excel(meme_database_path)

    def random_stickers(self, n: int) -> [str]:
        """Returns a random list of stickers

        Args:
            n (int): How much memes are required

        Returns:
            [str]: The list of the required stickers
        """
        ids = self.get_sticker_list("video")

        random.seed()
        random.shuffle(ids)
        for meme in ids:
            if "|" in meme:
                ids.remove(meme)
                for sub_sticker in meme.split("|"):
                    ids.append(sub_sticker.strip())
        selected_sticker = random.choice(ids)
        #logger.info(f"Choiced {selected_sticker}")
        return [selected_sticker]

    def search_stickers(self, query: str) -> [str]:
        """This function finds a meme andreturns his repective stickers

        Args:
            query (str): Meme to be found

        Returns:
            [str]: List of stickers ids to be used in inlinequery
        """
        query_words = into_words(query)
        dict_stickers = self.get_meme_list_dict()

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

    def get_meme_list_dict(self) -> dict:
        """Makes a dict with all the memes and stickers."""
        try:
            list_of_memes = self.meme_database_df["Meme"].tolist()
            list_of_stickers = self.meme_database_df["StickerID"].tolist()
            stickers_dict = {}
            for sticker, meme in zip(list_of_stickers, list_of_memes):
                if "video" not in sticker:
                    stickers_dict.update({sticker: [meme]})
            return stickers_dict
        except Exception:
            return {}

    def get_sticker_list(self, avoid_word: str = "") -> [str]:
        """Makes a list from all thestickers in excel

        Args:
            avoid_word: Specifies a word to be filtered in dataframe

        Returns:
            [str]: List of stickers
        """
        try:
            if avoid_word:
                filtered_dataframe = self.meme_database_df[~self.meme_database_df['StickerID'].str.contains(avoid_word)]
                filtered_dataframe_shuffled = filtered_dataframe.sample(frac=1)
                return filtered_dataframe_shuffled["StickerID"].tolist()
            else:
                return self.meme_database_df["StickerID"].tolist()
        except pd.errors.EmptyDataError:
            return []

    def get_meme_list(self) -> [str]:
        """Makes a list from all the memes in Excel

        Returns:
            [str]: List of memes
        """
        try:
            list_of_memes = self.meme_database_df["Meme"].tolist()
            return list_of_memes
        except Exception:
            return False

    def get_meme_list_summary(self) -> [str]:
        """Prepares the lists of the last memes to be sended as string

        Args:
            elements_from_last (int): How much elements are required

        Returns:
            str: The summary of memes
        """
        list_of_memes = self.get_meme_list()
        counter = 0
        summary = ""
        list_of_sublists = [list_of_memes[i:i + 50] for i in range(0, len(list_of_memes), 50)]
        list_of_summaries = []
        if list_of_memes:
            for sub_list in list_of_sublists:
                summary = ""
                for meme in sub_list:
                    counter += 1
                    summary += str(counter) + ". " + str(meme) + "\n"
                list_of_summaries.append(summary)
            return list_of_summaries
        else:
            return []

    def get_meme_sticker(self, meme_trigger: str) -> list | Any:
        """
        Find the sticker in excel and return its id

        :param meme_trigger: Meme phrase to search

        :return: List[str] | Any: Returns the id(s) of the sticker to be sent

        """

        self.load_dataframe()

        for _, meme_row in self.meme_database_df.iterrows():
            list_words = prepare_words(meme_row["Meme"])
            for sub_meme in list_words:
                if meme_trigger == sub_meme:
                    if "|" not in meme_row["StickerID"]:
                        return meme_row["StickerID"]
                    else:
                        return prepare_words(meme_row["StickerID"])
