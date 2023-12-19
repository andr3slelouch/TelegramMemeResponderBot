from llama_cpp import Llama
from config.config import load_config


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
            output = self.llm(prompt, self.max_tokens, self.stop)
            return output.get("choices", [{}])[0].get("text", "")
