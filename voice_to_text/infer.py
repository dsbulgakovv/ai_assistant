import speech_recognition as sr
import subprocess
import os
import logging
from logging.config import dictConfig

from log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("voice_to_text")


def convert_voice_to_text(path_to_file: str) -> str:
    path_to_wav_file = path_to_file[:-3] + 'wav'
    logger.info('Changing file format')
    logger.info(os.listdir('.'))
    logger.info(os.listdir('./service_files'))
    subprocess.call(['ffmpeg', '-i', path_to_file, path_to_wav_file])

    # Распознаем речь из аудио файла
    try:
        with sr.AudioFile(path_to_wav_file) as source:
            recognizer = sr.Recognizer()
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru")
    except sr.exceptions.UnknownValueError:
        logger.info('UnknownValueError - no text is recognized in the voice message.')
        text = '...'

    os.remove(path_to_file)
    os.remove(path_to_wav_file)

    return text


def main():
    cur_path = os.getcwd()
    print(cur_path)
    path_to_file = 'files/audio_AwACAgIAAxkBAAN4ZnslES-MBgVTaQZb4thG6WILAAH4AAIKUwACPnvZS6E9syBmndJnNQQ.mp3'
    text = convert_voice_to_text(path_to_file)
    print(text)


if __name__ == '__main__':
    main()
