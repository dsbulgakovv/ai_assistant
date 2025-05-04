FROM python:3.12

# Установка последней версии FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    flac  \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*


# Установка Poetry (фиксированная версия для стабильности)
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}
ENV PATH="/root/.local/bin:${PATH}"

# Настройка Poetry
RUN poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10

WORKDIR /app

COPY ./voice_to_text /app/
COPY pyproject.toml poetry.lock /app/

RUN mkdir service_files
# RUN apt-get install -y ffmpeg
RUN poetry install --no-interaction --no-ansi --without bot,large_lang_model,db

ENV PYTHONUNBUFFERED 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]