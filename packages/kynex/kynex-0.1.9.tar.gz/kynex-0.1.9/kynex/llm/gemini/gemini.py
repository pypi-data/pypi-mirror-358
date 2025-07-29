# import os
# import google.generativeai as genai
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class GeminiLLM(LLMBase):
#     def __init__(self):
#         genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#
#     def get_data(self, prompt: str, model_name: str = "gemini-1.5-flash") -> str:  # ✅ FIXED
#         try:
#             model = genai.GenerativeModel(model_name)
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#
#             response = model.generate_content(formatted_prompt)
#             return response.text
#         except Exception as e:
#             return f"[Gemini ERROR]: {str(e)}"


import google.generativeai as genai
from langchain_core.prompts import PromptTemplate
from kynex.llm.base import LLMBase

class GeminiLLM(LLMBase):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    def get_data(self, prompt: str) -> str:
        try:
            template = PromptTemplate.from_template("{prompt}")
            formatted_prompt = template.format(prompt=prompt)
            response = self.model.generate_content(formatted_prompt)
            print(response)
            return response.text
        except Exception as e:
            return f"[Gemini ERROR]: {str(e)}"
