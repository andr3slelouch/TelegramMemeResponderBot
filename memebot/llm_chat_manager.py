import logging

from llama_cpp import Llama
from config.config import load_config
from cysystemd.journal import JournaldLogHandler

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


class LlmChatManager:
    def __init__(self):
        config_data = load_config()
        model_path = config_data.get("llm_managing", {}).get("model_path", "")
        self.llm = Llama(model_path=model_path)
        self.max_tokens = config_data.get("llm_managing", {}).get("max_tokens", 1024)
        self.stop = config_data.get("llm_managing", {}).get("stop", [])

    def answer(self, message: str):
        config_data = load_config()
        prompt = config_data.get("llm_managing", {}).get("prompt", "")

        if prompt and "{MESSAGE}" in prompt:
            prompt = prompt.replace("{MESSAGE}", message)
            logger.info(f"Prompt: {prompt}")
            logger.info(f"max_tokens: {self.max_tokens}, stop: {self.stop}")
            output = self.llm(prompt, max_tokens=self.max_tokens, stop=self.stop)
            return output.get("choices", [{}])[0].get("text", "")
