from fastapi import FastAPI
from fastapi.responses import JSONResponse

import logging
from logging.config import dictConfig

from infer import convert_voice_to_text
from log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("voice_to_text")

app = FastAPI()


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to convert voice to text."})


@app.get("/voice_to_text")
async def voice_to_text(path_to_file: str):
    resp = convert_voice_to_text(path_to_file)
    return JSONResponse(content={"text": resp})
