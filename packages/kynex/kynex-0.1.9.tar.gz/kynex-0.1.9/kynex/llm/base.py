from abc import ABC, abstractmethod

class LLMBase(ABC):
    @abstractmethod
    def get_data(self, prompt: str, model_name: str = None) -> str:
        pass
