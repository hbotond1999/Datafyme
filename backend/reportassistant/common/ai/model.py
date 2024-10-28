import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


def get_llm_model(model: str = os.getenv("LLM_MODEL"), temperature: int = 0) -> BaseChatModel:
    """
    Args:
        model: The model identifier to be used. Defaults to the value of the "LLM_MODEL" environment variable.
        temperature: The temperature setting for the model that affects the randomness of responses. Defaults to 0.

    Returns:
        An instance of BaseChatModel specific to the LLM provider.
    """
    if os.getenv("LLM_PROVIDER") == "openai":
        return ChatOpenAI(model=model, temperature=temperature)