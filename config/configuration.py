import yaml
import os
import re
import sys
import logging
from shutil import copyfile
from pathlib import Path


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


def get_file_location(filename: str) -> str:
    """This function gets the full path location of a file

    Args:
        filename (str): Filename that needs the full path location

    Returns:
        full_path_file_location (str): Full path location of the file
    """
    working_directory = get_working_directory()
    full_path_file_location = os.path.join(working_directory, filename)
    return full_path_file_location


def get_video_location(filename: str) -> str:
    working_directory = get_working_directory()
    working_directory = os.path.join(working_directory, "videos")
    full_path_file_location = os.path.join(working_directory, filename)
    return full_path_file_location


logging.basicConfig(
    filename=get_file_location("Running.log"),
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def load_config_file(config_file_path: str) -> dict:
    """This function is for loading yaml config file

    Args:
        config_file_path (str): File path for the config file to be loaded

    Returns:
        file_config (dict): Dictionary with config keys.

    Raises:
        IOError
    """
    try:
        with open(get_file_location(config_file_path), "r") as config_yaml:
            file_config = yaml.safe_load(config_yaml)
            return file_config
    except IOError:
        logging.error("Archivo de configuración no encontrado, generando llaves")


def generate_bot_token_file(config_file_path: str):
    """This function generates a db selector file template with the required parameters

    Args:
        config_file_path (str): Where the file should be stored
    """
    db_selector = {
        "token_bot": "",
    }
    with open(config_file_path, "w") as f:
        f.write(yaml.safe_dump(db_selector, default_flow_style=False))


def get_bot_token(config_file_path: str) -> str:
    """Returns the bot token stored in config_file_path

    Args:
        config_file_path (str): Where the file is stored

    Returns:
        str: Token to access to Telegram Bot
    """
    try:
        with open(get_file_location(config_file_path), "r") as config_yaml:
            file_config = yaml.safe_load(config_yaml)
            return file_config["token_bot"]
    except IOError:
        print("Archivo de configuración no encontrado, generando archivo")
        generate_bot_token_file(config_file_path)


def set_bot_token(config_file_path: str, token: str):
    """Saves the telegram token for being used for the bot telegram

    Args:
        config_file_path (str): Where the file is stored
        token (str): A valid token to access to Telegram Bot

    """
    try:
        with open(get_file_location(config_file_path), "r") as config_yaml:
            file_config = yaml.safe_load(config_yaml)
    except IOError:
        print("Archivo de configuración no encontrado, generando archivo")
        generate_bot_token_file(config_file_path)
    file_config["token_bot"] = token
    with open(config_file_path, "w") as f:
        f.write(yaml.safe_dump(file_config, default_flow_style=False))
