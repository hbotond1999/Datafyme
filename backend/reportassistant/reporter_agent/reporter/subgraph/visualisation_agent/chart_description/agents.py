from langchain_core.prompts import PromptTemplate
from reporter_agent.reporter.subgraph.visualisation_agent.chart_description.response import ChartDescription

from common.ai.model import get_llm_model


def chart_description_agent():
    """
    Creates an agent to write descriptions for charts.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """
    prompt_str = """Your task is to provide a description of the following figure, which you receive as a base64 encoded 
    image as input: {chart_png}
    
    You can use the summary of the chart's data source for the description, which we created with the df.summarize 
    command.
    Summarized data: {summary}
    
    Write a descriptive summary of the figure, stating
    - what is shown in the figure?
    - what conclusions can be drawn from the figure?
    - what are the main descriptive statistics?
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["chart_png", "summary"])

    return prompt | get_llm_model().with_structured_output(ChartDescription)
