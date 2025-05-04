import json

from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()


# Definiáljuk a kérés modelljét
class PandasCodeRequest(BaseModel):
    data_json: str
    code: str


@app.post("/run_pandas_code")
async def run_pandas_code(request: PandasCodeRequest):
    import pandas as pd

    # Convert JSON to DataFrame
    try:
        df = pd.read_json(request.data_json, orient='records', convert_dates=True)
    except Exception as e:
        return Response(status_code=400, content=f"Error parsing JSON data: {str(e)}")

    # Execute the code
    try:
        exec(request.code, {"df": df, "pd": pd})
    except Exception as e:
        return Response(status_code=500, content=str(e))

    # Convert DataFrame back to JSON
    try:
        result_json = df.to_json(orient='records', date_format='iso')
        return JSONResponse(content=json.loads(result_json))
    except Exception as e:
        return Response(status_code=500, content=f"Error converting result to JSON: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8050)