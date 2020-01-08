FROM python:3.7-slim-buster

LABEL maintainer="Dennis Muth <d.muth@gmx.net>"

ENV CONFIGPATH=/config \
    PYTHONPATH=/homebot \
    WORKDIR=/homebot

# Create directory structure
RUN mkdir -p ${WORKDIR}

WORKDIR ${WORKDIR}

# Copy build scripts
COPY docker/ docker/
RUN docker/setup_prereqs

# Copy poetry project configuration and lock file
COPY pyproject.toml poetry.lock ./

RUN poetry install --no-dev

COPY . .

CMD ["poetry", "run", "python", "homebot", "run", "/config/run.py"]
