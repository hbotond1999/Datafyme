import pandas as pd

from reporter_agent.reporter.agents import dataframe_date_decider, logger


def convert_pandas_columns(df):
    columns_types = dataframe_date_decider().invoke({"dataframe": df.head(n=50).to_dict("list")})
    for column_info in columns_types["column_types"]:
        column_name = column_info["name"]
        recommended_type = column_info["recommended_type"]

        if column_name not in df.columns:
            continue

        if recommended_type == "string":
            df[column_name] = df[column_name].astype(str)
        elif recommended_type == "int":
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce').astype(int)
        elif recommended_type == "float":
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce').astype(float)
        elif recommended_type in ["date", "datetime"]:
            parsing_format = column_info.get("parsing_format")
            if parsing_format:
                df[column_name] = pd.to_datetime(df[column_name], format=parsing_format, errors='coerce')
            else:
                df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
        elif recommended_type == "bool":
            try:
                df[column_name] = df[column_name].astype(bool)
            except Exception as e:
                logger.info("Bool conversion failed")
    return df