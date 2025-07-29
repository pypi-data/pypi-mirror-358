# from kynex.main.llm_connector import LLMConnector
#
# class Kynex:
#     @staticmethod
#     def get_llm_response(prompt: str, model_name: str = None) -> str:
#         connector = LLMConnector()
#         return connector.getLLMData(prompt, model_name)
from kynex.llm_connector import LLMConnector


class Kynexa:
    LLM_GEMINI = "gemini"
    LLM_GROQ = "groq"
    @staticmethod
    def get_llm_response(prompt: str, model_name: str, api_key: str, llm_type: str = None) -> str:

        if llm_type is None:
            llm_type = Kynexa.LLM_GEMINI
        connector = LLMConnector(api_key=api_key, model_name=model_name, llm_type=llm_type)
        return connector.getLLMData(prompt)


