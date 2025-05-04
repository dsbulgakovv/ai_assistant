FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry (фиксированная версия для стабильности)
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}
ENV PATH="/root/.local/bin:${PATH}"

# Настройка Poetry
RUN poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10

WORKDIR /app

COPY ./database /app/
COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-interaction --no-ansi --no-root --without bot,large_lang_model,voice_to_text

CMD ["poetry", "run", "python", "init_db.py"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
