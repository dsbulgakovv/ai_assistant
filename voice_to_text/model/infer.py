import speech_recognition as sr
import subprocess
import os


def convert_voice_to_text(path_to_file: str):
    path_to_wav_file = path_to_file[:-3] + 'wav'
    subprocess.call(['ffmpeg', '-i', path_to_file, path_to_wav_file])

    # Распознаем речь из аудио файла
    with sr.AudioFile(path_to_wav_file) as source:
        recognizer = sr.Recognizer()
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="ru")

    return text


def main():
    cur_path = os.getcwd()
    print(cur_path)
    path_to_file = 'files/audio_AwACAgIAAxkBAAN4ZnslES-MBgVTaQZb4thG6WILAAH4AAIKUwACPnvZS6E9syBmndJnNQQ.mp3'
    text = convert_voice_to_text(path_to_file)
    print(text)


if __name__ == '__main__':
    main()
