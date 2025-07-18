from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from reporter_agent.reporter.subgraph.visualisation_agent.ai import RepType
from reporter_agent.reporter.subgraph.visualisation_agent.chart import ChartTypes


def create_representation_agent():
    """
    Creates a representation agent for data science tasks.

    The function generates a prompt string by listing all available representation types from the RepType enumeration. It then prepares a prompt template that includes the user's question and preview data. Finally, it returns the constructed prompt that is connected to the language model.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """
    rep_types = ", ".join([rep.value for rep in RepType])
    prompt_str = f"""You are a professional data scientist. Your task is to decide how to represent the data. This options are available: {rep_types}
    
    """ + """  
Guidelines:
- Prefer a chart when it helps to visualize the data more clearly.
- Choose the representation type that best supports answering the user's question.
- Your answer must contain only **one** of the available representation types — no explanations or extra text.

USER QUESTION:
{question}

DATA PREVIEW:
{preview_data}
"""

    prompt = PromptTemplate(template=prompt_str, input_variables=["preview_data", "question"])

    return prompt | get_llm_model()


def create_chart_selector_agent():
    """
    Creates a chart selector agent that helps in determining the appropriate chart type for given data.

    The function constructs a prompt that asks a data scientist to decide which chart to use to represent the data
    based on available options. It then returns a composed prompt with an LLM model to provide the appropriate chart selection.

    Returns:
        PromptTemplate: A template containing the structured prompt and input variables.
    """
    prompt_str = (f"You are a professional data scientist. Your task is to decide which chart to use to represent the "
                  f"data. This options are available: {", ".join([c_type.value for c_type in ChartTypes])}")

    prompt_str += """"
    
    USER question: {question}
    
    DATA: {preview_data}

    Your answer only contains one of the options.
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["preview_data", "question"])

    return prompt | get_llm_model()


def create_chart_def_agent(structured_output):
    """
    Args:
        structured_output: The specified structure for model outputs used to generate the chart definitions.

    Returns:
        An instance of PromptTemplate filled with the relevant input variables and connected to the language model with structured output configuration.
    """
    prompt_str = """Previously, you selected this {chart_type} for representing this data: {preview_data}
    
     USER question: {question}
    
     Your task is to assist in creating the visualization. To do this, label each axis of the chart with the column names according to the provided structure. 
     
     Please select the column names exactly as they appear in the attached dataset. 
     
     The title must be in this language {language}
    """
    prompt = PromptTemplate(template=prompt_str, input_variables=["preview_data", "chart_type", "question", "language"])

    return prompt | get_llm_model().with_structured_output(structured_output)


def create_chart_def_fix_agent(structured_output):
    prompt_str = """"Based on previous interactions, you selected a {chart_type} chart for this dataset: {preview_data}.
    
    The chart was initially structured as follows:
    {selected_chart_structure}
    
    However, the following validation errors were encountered:
    {error_messages}
    
    Please provide a corrected version of the chart structure.
    
     The title must be in this language {language}
    """
    prompt = PromptTemplate(template=prompt_str, input_variables=["chart_type", "preview_data", "error_messages", "selected_chart_structure", "language"])

    return prompt | get_llm_model().with_structured_output(structured_output)


def create_summarize_agent():
    prompt_str = """
   You are a helpful assistant, and your task is to summarize the following data in a response. You must response the following language: {language}
   
   User's question:  {question}
   
   USER question: {data}
   """

    prompt = PromptTemplate(template=prompt_str, input_variables=["data", "question", "language"])

    return prompt | get_llm_model()