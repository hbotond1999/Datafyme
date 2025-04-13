import os
import pickle
from io import BytesIO

import pandas as pd
import requests

from db_configurator.ai.data_cleaner.agents import dataframe_cleaner_agent


def cleaning_pandas_df(df):
    df = df.fillna(value=None, method='ffill')
    code = dataframe_cleaner_agent().invoke({"dataframe": df.head(n=50).to_dict("list")})
    df = run_pandas_code_on_server(df, code.code)
    return df


def run_pandas_code_on_server(dataframe: pd.DataFrame, code: str):
    """
    Send a pandas DataFrame and Python code to the server for execution.

    Args:
        dataframe (pd.DataFrame): The DataFrame to process
        code (str): Python code to execute on the DataFrame
        url (str): The URL of the server endpoint

    Returns:
        pd.DataFrame: The resulting DataFrame after code execution
    """
    pickle_buffer = BytesIO()
    pickle.dump(dataframe, pickle_buffer)
    pickle_buffer.seek(0)

    files = {
        'data_file': ('dataframe.pkl', pickle_buffer.getvalue(), 'application/octet-stream')
    }
    form_data = {
        'code': code
    }

    # Send the request to the server
    url = os.getenv("CODE_RUNNER_SERVER")
    response = requests.post(url + "/run_pandas_code", files=files, data=form_data)

    if response.status_code == 200:
        result_df = pickle.loads(response.content)
        return result_df
    else:
        raise Exception(f"Server error: {response.text}")