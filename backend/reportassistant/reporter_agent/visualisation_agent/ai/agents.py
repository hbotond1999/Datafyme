from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from reporter_agent.visualisation_agent.ai import RepType
from reporter_agent.visualisation_agent.chart import ChartTypes


def create_representation_agent():

        rep_types = ", ".join([rep.value for rep in RepType])
        prompt_str = f"""You are a professional data scientist. Your task is to decide how to represent the data. This options are available: {rep_types}
        """ + """
        DATA: {preview_data}
        
        Your answer only contains one of the options.
        """

        prompt = PromptTemplate(template=prompt_str, input_variables=["preview_data"])

        return prompt | get_llm_model()


def create_chart_selector_agent():
    prompt_str = (f"You are a professional data scientist. Your task is to decide which chart to use to represent the "
                  f"data. This options are available: {", ".join([c_type.value for c_type in ChartTypes])}")

    prompt_str += """"
    DATA: {preview_data}

    Your answer only contains one of the options.
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["preview_data"])

    return prompt | get_llm_model()


def create_chart_def_agent(structured_output):
    prompt_str = """Previously, you selected this {chart_type} for representing this data: {preview_data}
    
     Your task is to assist in creating the visualization. To do this, label each axis of the chart with the column names according to the provided structure.
      """

    prompt = PromptTemplate(template=prompt_str, input_variables=["preview_data", "chart_type"])

    return prompt | get_llm_model().with_structured_output(structured_output)
