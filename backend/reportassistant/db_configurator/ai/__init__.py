import json
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
    Send a pandas DataFrame and Python code to the server for execution using JSON.

    Args:
        dataframe (pd.DataFrame): The DataFrame to process
        code (str): Python code to execute on the DataFrame

    Returns:
        pd.DataFrame: The resulting DataFrame after code execution
    """
    # Convert DataFrame to JSON
    json_data = dataframe.to_json(orient='records', date_format='iso')

    # Prepare the request
    data = {
        'data_json': json_data,
        'code': code
    }

    # Send the request to the server
    url = os.getenv("CODE_RUNNER_SERVER")
    response = requests.post(url + "/run_pandas_code", json=data)

    if response.status_code == 200:
        # Convert JSON response back to DataFrame
        result_json = response.json()
        result_df = pd.read_json(json.dumps(result_json), orient='records', convert_dates=True)
        return result_df
    else:
        raise Exception(f"Server error: {response.text}")