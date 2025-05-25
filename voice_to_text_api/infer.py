import os
import logging
from logging.config import dictConfig

# import speech_recognition as sr
import subprocess

from deepgram import DeepgramClient, PrerecordedOptions, FileSource

from log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("voice_to_text")


# def convert_voice_to_text(path_to_file: str) -> str:
#     path_to_wav_file = path_to_file[:-3] + 'wav'
#     logger.info('Changing file format')
#     logger.info(os.listdir('.'))
#     logger.info(os.listdir('./service_files'))
#     subprocess.call(['ffmpeg', '-i', path_to_file, path_to_wav_file])
#
#     # Распознаем речь из аудио файла
#     try:
#         with sr.AudioFile(path_to_wav_file) as source:
#             recognizer = sr.Recognizer()
#             audio_data = recognizer.record(source)
#             logger.info('Audio data is built!')
#             text = recognizer.recognize_google(audio_data, language="ru")
#             logger.info('Audio data is transformed to text!')
#     except sr.exceptions.UnknownValueError:
#         logger.info('UnknownValueError - no text is recognized in the voice message.')
#         text = '...'
#     except Exception as e:
#         logger.info(f'Error: {e}')
#     finally:
#         os.remove(path_to_file)
#         os.remove(path_to_wav_file)
#
#     return text


# def convert_voice_to_text(path_to_file: str, model) -> str:
#     logger.info('Converting voice to text ...')
#     try:
#         result = model.transcribe(path_to_file, language="ru")
#         return result["text"] if result["text"] else '...'
#     except Exception as e:
#         logger.info(f'Error: {e}')
#     finally:
#         os.remove(path_to_file)


async def convert_voice_to_text(deepgram: DeepgramClient, options: PrerecordedOptions, path_to_file: str) -> str:
    logger.info('Converting voice to text ...')
    try:
        # path_to_wav_file = path_to_file[:-3] + 'wav'
        # logger.info('Changing file format')
        # logger.info(os.listdir('.'))
        # logger.info(os.listdir('./service_files'))
        # subprocess.call(['ffmpeg', '-i', path_to_file, path_to_wav_file])
        with open(path_to_file, "rb") as file:
            buffer_data = file.read()
        payload: FileSource = {
            "buffer": buffer_data,
        }
        response = await deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        text = response.to_json()['results']['channels'][0]['alternatives'][0]['transcript']
        return text if text else '...'
    except Exception as e:
        logger.info(f'Error: {e}')
    finally:
        os.remove(path_to_file)


def main():
    cur_path = os.getcwd()
    print(cur_path)
    path_to_file = 'files/audio_AwACAgIAAxkBAAN4ZnslES-MBgVTaQZb4thG6WILAAH4AAIKUwACPnvZS6E9syBmndJnNQQ.mp3'
    text = convert_voice_to_text(path_to_file)
    print(text)


if __name__ == '__main__':
    main()
