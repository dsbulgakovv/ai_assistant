FROM python:3.12

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY ./daatabase /app/

COPY pyproject.toml poetry.lock /app/
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --no-root --without bot,large_lang_model,voice_to_text,dev


CMD ["poetry", "run", "python", "init-script.py"]