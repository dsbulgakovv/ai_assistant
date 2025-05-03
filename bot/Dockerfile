FROM python:3.12-slim

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN mkdir service_files
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --without voice_to_text,large_lang_model


COPY ./bot /app/

CMD ["python", "app.py"]