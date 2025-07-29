from groq import Groq
from langchain_core.prompts import PromptTemplate
from kynex.llm.base import LLMBase

class GroqLLM(LLMBase):
    def __init__(self, api_key: str, model_name: str):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def get_data(self, prompt: str) -> str:
        try:
            # Optional: format prompt using LangChain template
            template = PromptTemplate.from_template("{prompt}")
            formatted_prompt = template.format(prompt=prompt)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": formatted_prompt}],
                temperature=0.7
            )
            print(response)

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Groq ERROR]: {str(e)}"
