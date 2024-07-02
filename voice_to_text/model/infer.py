import speech_recognition as sr
import subprocess
import logging
import os


def convert_voice_to_text(path_to_file: str, log: logging.getLogger()) -> str:
    path_to_wav_file = path_to_file[:-3] + 'wav'
    log.info('Changing file format')
    log.info(os.listdir('.'))
    log.info(os.listdir('./service_files'))
    subprocess.call(['ffmpeg', '-i', path_to_file, path_to_wav_file])

    # Распознаем речь из аудио файла
    with sr.AudioFile(path_to_wav_file) as source:
        recognizer = sr.Recognizer()
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="ru")

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
