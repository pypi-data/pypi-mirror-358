# 🔷 Kynex

**Kynex** is a modular Python framework that simplifies connecting to multiple LLM providers such as **Google Gemini** and **Groq** via a unified, flexible interface. Whether you're building AI workflows, chatbots, or prompt-based applications, Kynex makes it seamless to integrate LLMs dynamically based on user input.

---

## 🚀 Features

-  Multi-LLM support**: Easily switch between different LLMs
-  API key flexibility**: Dynamically accept LLM type, model name, and API key at runtime
-  LangChain prompt integration**: Use `PromptTemplate` for advanced prompt formatting
-  Simple base architecture**: Extend to any new LLM provider with a custom class


---

## 📦 Installation

```bash
pip install kynex


Example Usage:

Create it:

Create a Python file and add the following:

from kynex.kynexa import Kynex

request = {
    "prompt": "your_prompt.",
    "model_name": "your_model_name",
    "api_key": "your_api_key",
    "llm_type": "type_llm"  # e.g: "gemini"
}

response = Kynex.get_llm_response(
    prompt=request["prompt"],
    model_name=request["model_name"],
    api_key=request["api_key"],
    llm_type=request.get("llm_type")
)

print(response)
