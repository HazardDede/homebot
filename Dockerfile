#
# Notice: Keep this file in sync with Dockerfile.arm32v7
#

FROM python:3.7-slim-stretch

LABEL maintainer="Dennis Muth <d.muth@gmx.net>"

ENV WORKDIR=/homebot \
    PYTHONPATH=/homebot

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

CMD ["poetry", "run", "python", "homebot", "run", "./configs/prod.py"]
