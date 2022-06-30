FROM python:3.10

RUN apt-get update && apt-get upgrade -y &&  rm -rf /var/lib/apt/lists/*

WORKDIR /karez

ENV PYTHONPATH="${PYTHONPATH}:/karez/" \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

COPY pyproject.toml /karez/
COPY karez /karez/karez

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -vvv --no-dev --no-interaction --no-ansi

ENTRYPOINT ["karez"]