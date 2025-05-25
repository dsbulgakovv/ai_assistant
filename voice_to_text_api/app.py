from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

# from functools import lru_cache
import os

# import whisper
from deepgram import DeepgramClient, ClientOptionsFromEnv, PrerecordedOptions

import logging
from logging.config import dictConfig

from infer import convert_voice_to_text
from log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("voice_to_text")

app = FastAPI()


MODEL_CACHE_DIR = "/app/models/whisper_cache"
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = MODEL_CACHE_DIR
deepgram_api_token = os.getenv('DEEPGRAM_ASR_API_KEY')

deepgram = DeepgramClient("", ClientOptionsFromEnv(api_key=deepgram_api_token))
options = PrerecordedOptions(
    model="nova-2",
    language="ru",
    smart_format=True,
)


# @lru_cache(maxsize=None)
# def load_whisper_model():
#     logger.info('Loading the model ...')
#     return whisper.load_model("small")


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to convert voice to text."})


# @app.get("/voice_to_text")
# async def voice_to_text(path_to_file: str, model=Depends(load_whisper_model)):
#     resp = convert_voice_to_text(path_to_file, model)
#     return JSONResponse(content={"text": resp})


@app.get("/voice_to_text")
async def voice_to_text(path_to_file: str):
    resp = convert_voice_to_text(deepgram, options, path_to_file)
    return JSONResponse(content={"text": resp})
