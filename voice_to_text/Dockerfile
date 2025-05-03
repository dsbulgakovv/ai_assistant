FROM python:3.12-slim

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

RUN poetry config virtualenvs.create false

WORKDIR /voice_to_text

COPY pyproject.toml poetry.lock /voice_to_text/
RUN mkdir service_files
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --without bot,large_lang_model

COPY ./voice_to_text /voice_to_text/

ENV PYTHONUNBUFFERED 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]