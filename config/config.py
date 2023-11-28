# config/config.py
import os

import yaml


def load_config():
    with open('../config/config.yml', 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data


def get_video_location(filename: str) -> str:
    working_directory = get_working_directory()
    working_directory = os.path.join(working_directory, "videos")
    full_path_file_location = os.path.join(working_directory, filename)
    return full_path_file_location


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
