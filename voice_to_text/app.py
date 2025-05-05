from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from functools import lru_cache

import whisper

import logging
from logging.config import dictConfig

from infer import convert_voice_to_text
from log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("voice_to_text")

app = FastAPI()


@lru_cache(maxsize=None)
def load_whisper_model():
    return whisper.load_model("small")


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to convert voice to text."})


@app.get("/voice_to_text")
async def voice_to_text(path_to_file: str, model=Depends(load_whisper_model)):
    resp = convert_voice_to_text(path_to_file, model)
    return JSONResponse(content={"text": resp})
