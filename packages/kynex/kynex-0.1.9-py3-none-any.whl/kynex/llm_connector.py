import os
import configparser

# from kynex.llm.gemini.gemini import GeminiLLM
# from kynex.llm.groq.groq import DeepSeekLLM
#
# class LLMConnector:
#     def __init__(self):
#         self.llm_type = self.load_llm_type()
#
#     def load_llm_type(self):
#         config = configparser.ConfigParser()
#         config.read(os.path.abspath("resources/kynex.properties"))
#         return config.get("DEFAULT", "llm", fallback="gemini").lower()
#
#     def get_llm_instance(self):
#         if self.llm_type == "gemini":
#             return GeminiLLM()
#         elif self.llm_type == "groq":
#             return DeepSeekLLM()
#         else:
#             raise ValueError(f"Unsupported LLM type: {self.llm_type}")
#
#     def getLLMData(self, prompt: str, model_name: str = None) -> str:
#         llm = self.get_llm_instance()
#         return llm.get_data(prompt, model_name)

from kynex.llm.gemini.gemini import GeminiLLM
from kynex.llm.groq.groq import GroqLLM


class LLMConnector:
    def __init__(self, api_key: str, model_name: str, llm_type: str = "gemini"):
        self.llm_type = llm_type.lower() if llm_type else "gemini"
        self.api_key = api_key
        self.model_name = model_name

    def get_llm_instance(self):
        if self.llm_type == "gemini":
            return GeminiLLM(api_key=self.api_key, model_name=self.model_name)
        elif self.llm_type == "groq":
            return GroqLLM(api_key=self.api_key, model_name=self.model_name)
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")

    def getLLMData(self, prompt: str) -> str:
        llm = self.get_llm_instance()
        return llm.get_data(prompt)
