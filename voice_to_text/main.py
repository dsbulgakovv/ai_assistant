from fastapi import FastAPI
from fastapi.responses import JSONResponse

from model.infer import convert_voice_to_text


app = FastAPI()


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to convert voice to text."})


@app.get("/voice_to_text")
async def voice_to_text(path_to_file: str):
    resp = convert_voice_to_text(path_to_file)

    return JSONResponse(content={"text": resp})
