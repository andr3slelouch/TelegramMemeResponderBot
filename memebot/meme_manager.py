import random
from collections import OrderedDict
from typing import Any

import pandas as pd

from config.config import load_config
from utils.utils import prepare_words


class MemeManager:
    meme_database_df = None

    def __init__(self):
        self.meme_database_df = None
        self.load_dataframe()

    def load_dataframe(self) -> None:
        if self.meme_database_df is None:
            config_data = load_config()
            meme_database_path = config_data.get("meme_managing", {}).get("meme_database", "")
            self.meme_database_df = pd.read_excel(meme_database_path)

    def random_stickers(self,n: int) -> [str]:
        """Returns a random list of stickers

        Args:
            n (int): How much memes are required

        Returns:
            [str]: The list of the required stickers
        """
        ids = self.get_sticker_list()
        random.shuffle(ids)
        """
        for meme in ids:
            if "|" in meme:
                ids.remove(meme)
                for sub_sticker in meme.split("|"):
                    ids.append(sub_sticker.strip())
        
        """
        ids = [sub_sticker.strip() for meme in ids if "|" in meme for sub_sticker in meme.split("|")]
        return list(OrderedDict.fromkeys(ids[:n]))

    def get_sticker_list(self) -> [str]:
        """Makes a list from all thestickers in excel

        Returns:
            [str]: List of stickers
        """
        try:
            return self.meme_database_df["StickerID"].tolist()
        except pd.errors.EmptyDataError:
            return []

    def get_meme_sticker(self, meme_trigger: str) -> list | Any:
        """
        Find the sticker in excel and return its id

        :param meme_trigger: Meme phrase to search

        :return: List[str] | Any: Returns the id(s) of the sticker to be sent

        """
        # TODO REFACTORIZE FOR TO ONELINE FOR

        self.load_dataframe()

        for _, meme_row in self.meme_database_df.iterrows():
            list_words = prepare_words(meme_row["Meme"])
            for sub_meme in list_words:
                if meme_trigger == sub_meme:
                    if "|" not in meme_row["StickerID"]:
                        return meme_row["StickerID"]
                    else:
                        return prepare_words(meme_row["StickerID"])
