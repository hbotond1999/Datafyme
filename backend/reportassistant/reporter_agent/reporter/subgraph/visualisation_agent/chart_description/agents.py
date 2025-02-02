from langchain_core.prompts import PromptTemplate

from reporter_agent.reporter.subgraph.visualisation_agent.chart_description.response import ChartDescription

from common.ai.model import get_llm_model


def chart_description_agent():
    """
    Creates an agent to write descriptions for charts.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """
    prompt_str = """
    {message}
    You can additionally use the chart's data source summary for a more precise description.
    Summarized data: {summary}
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["message", "summary"])

    return prompt | get_llm_model().with_structured_output(ChartDescription)
