from fastapi import FastAPI
from fastapi.responses import JSONResponse

from typing import Any

from model.infer import convert_voice_to_text


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Service to convert voice to text."}


@app.get("/voice_to_text")
async def voice_to_text(audio_obj: Any):
    resp = convert_voice_to_text(audio_obj)

    return JSONResponse(content={"text": resp})
