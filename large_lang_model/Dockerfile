FROM python:3.12

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

RUN poetry config virtualenvs.create false

WORKDIR /large_lang_model

COPY pyproject.toml poetry.lock /large_lang_model/
RUN mkdir artifacts
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --without bot,voice_to_text

COPY ./large_lang_model /large_lang_model/

ENV PYTHONUNBUFFERED 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]