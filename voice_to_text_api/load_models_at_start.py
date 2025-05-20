import whisper
import os


def main():
    MODEL_CACHE_DIR = "/app/models/whisper_cache"
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
    os.environ["XDG_CACHE_HOME"] = MODEL_CACHE_DIR

    whisper.load_model('small')
    whisper.load_model("tiny")


if __name__ == '__main__':
    main()
