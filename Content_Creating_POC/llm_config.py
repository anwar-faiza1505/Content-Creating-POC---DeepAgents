import os
from langchain_openai import ChatOpenAI
from token import token_generation


def get_model(model_name: str = "gpt-4o"):
    """Return a configured llm for the given model name"""
    return ChatOpenAI(
        model_name=model_name,
        default_headers = {"Authorisation": f"Bearer {token_generation()}"},
        openai_api_base=os.getenv("OPENAI_API_BASE"),
    )