from fastapi import FastAPI
from fastapi.responses import JSONResponse

import logging
from logging.config import dictConfig

from infer import infer_llm
from log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("large_lang_model")

app = FastAPI()


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to convert voice to text."})


@app.get("/answer_me_llm")
async def voice_to_text(inp_text: str):
    resp = infer_llm(inp_text)
    return JSONResponse(content={"text": resp})
