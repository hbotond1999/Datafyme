import os

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from reporter_agent.models import GenAIModel


def get_llm_model(temperature: int = 0) -> BaseChatModel:
    """
    Args:
        temperature: The temperature setting for the model that affects the randomness of responses. Defaults to 0.

    Returns:
        An instance of BaseChatModel specific to the LLM provider.
    """
    model = GenAIModel.objects.get(active=True)
    if model.provider == "openai":
        return ChatOpenAI(model=model.name, api_key=model.api_key, temperature=temperature)

    if model.provider == "claude":

        return ChatAnthropic(
            model=model.name,
            api_key=model.api_key,
            temperature=temperature,
        )

    if model.provider == "google":
        return ChatGoogleGenerativeAI(
            model=model.name,
            api_key=model.api_key,
            max_output_tokens=10
        )

    raise Exception("Unknown model provider")