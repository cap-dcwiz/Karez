FROM python:3.11 as build

ENV PYTHONPATH="${PYTHONPATH}:/opt/" \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /opt

COPY ./ /opt/

RUN apt-get update && apt-get upgrade -y && \
    apt-get install build-essential -y && \
    poetry install && poetry build -f wheel

FROM python:3.11

ENV PYTHONPATH="${PYTHONPATH}:/opt/" \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

COPY --from=build /opt/dist/*.whl /opt/

WORKDIR /opt

RUN apt-get update && apt-get upgrade -y && \
    apt-get install build-essential -y && \
    pip install *.whl && \
    apt-get purge build-essential -y && rm -rf /var/lib/apt/lists/* && \
    rm /opt/*.whl