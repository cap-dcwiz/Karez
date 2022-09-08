FROM python:3.10

RUN apt-get update && apt-get upgrade -y &&  rm -rf /var/lib/apt/lists/*

WORKDIR /karez

ENV PYTHONPATH="${PYTHONPATH}:/karez/" \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml /karez/
RUN poetry install -vvv --no-dev --no-interaction --no-ansi

COPY karez /karez/karez
RUN poetry install -vvv --no-dev --no-interaction --no-ansi && \
    rm /karez/poetry.lock /karez/pyproject.toml

ENTRYPOINT ["karez"]