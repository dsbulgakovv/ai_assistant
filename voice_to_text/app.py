import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import logging
from logging.config import dictConfig

from model.infer import convert_voice_to_text
from model.log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("voice_to_text")

logger.info(os.listdir('./service_files'))
logger.info(os.listdir('.'))
logger.info(os.listdir('../'))
logger.info(os.getcwd())

app = FastAPI()


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to convert voice to text."})


@app.get("/listdir")
async def root(path_dir: str):
    content = ' '.join(os.listdir(path_dir))
    return JSONResponse(content={"message": content})


@app.get("/voice_to_text")
async def voice_to_text(path_to_file: str):
    resp = convert_voice_to_text(path_to_file)
    return JSONResponse(content={"text": resp})
