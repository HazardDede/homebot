FROM python:3.7-slim-buster@sha256:4f9bc56882e218da1b0bd9152a8a4b048592631cf25795cec0dfe0ed55ceb1c8
COPY qemu-arm-static /usr/bin

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

RUN docker/install_deps

COPY . .

CMD ["python", "homebot", "run", "/config/run.py"]
