# config/config.py
import os

import yaml


def load_config():
    with open('../config/config.yml', 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data


def get_video_location(filename: str) -> str:
    """
    This method generates a video full path
    :param filename: Filename to generate a path
    :return: string with the full path
    """
    config_data = load_config()
    parent_path = config_data.get("meme_managing", {}).get("meme_video_path", "")
    if parent_path:
        full_path_file_location = os.path.join(parent_path, filename)
        return full_path_file_location
    else:
        raise FileNotFoundError


def get_working_directory() -> str:
    """This functions gets the working directory path.

    Returns:
        working_directory (str): The directory where database and yaml are located.
    """
    userdir = os.path.expanduser("~")
    working_directory = os.path.join(userdir, "MemeBot")
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
    return working_directory


def get_telegram_credentials():
    # Retrieve and return Telegram bot credentials
    pass
