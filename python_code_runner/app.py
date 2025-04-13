import io

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import Response
import pickle
import uvicorn
app = FastAPI()

@app.post("/run_pandas_code")
async def run_pandas_code(
    data_file: UploadFile = File(...),
    code: str = Form(...)
):
    contents = await data_file.read()
    df = pickle.loads(contents)

    import pandas as pd

    try:
        exec(code, {"df": df, "pd": pd})
    except Exception as e:
        return Response(status_code=500, contents=str(e))

    pickle_buffer = io.BytesIO()
    pickle.dump(df, pickle_buffer)
    pickle_buffer.seek(0)

    return Response(
        content=pickle_buffer.getvalue(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=result.pkl"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8050)
