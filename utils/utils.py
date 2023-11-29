import re
from unicodedata import normalize


def word_count(string):
    # Here we are removing the spaces from start and end,
    # and breaking every word whenever we encounter a space
    # and storing them in a list. The len of the list is the
    # total count of words.
    return len(string.strip().split(" "))


def prepare_words(string) -> list:
    """This function prepare a string that has | in his content and split in a list

    Args:
        string: Wort to be splitted

    Returns:
        list: A list that contains the string splitted in a list
    """
    list_words = string.strip().split("|")
    return [word.strip() for word in list_words]


def string_normalizer(phrase: str) -> str:
    """This functions is made for clean any character different to ascii

    Args:
        phrase (str): Phrase to be normalized

    Returns:
        str: Normalized string to be compared to memes in list
    """
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


def process_video_parameters_to_dict(video_parameters_list: [str]) -> dict:
    video_parameters_dict = {}
    for video_parameter in video_parameters_list:
        video_parameter_list = video_parameter.split(":")
        video_parameters_dict[video_parameter_list[0]] = video_parameter_list[1]
    return video_parameters_dict


def into_words(q: str) -> [str]:
    """This function split a string to his characters

    Args:
        q (str): String to be splitted

    Returns:
        [str]: List of characters
    """
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
    """Returns if a word exists inside the list of words

    Args:
        word (str): Word to be finded
        words ([str]): List of words

    Returns:
        bool: Returns True if the word is found else False
    """
    for w in words:
        if w.startswith(word):
            return True
    return False
