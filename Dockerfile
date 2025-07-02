FROM python:3.12.1-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG GITEA_TOKEN_NAME
ARG GITEA_TOKEN

ENV GITEA_TOKEN_NAME ${GITEA_TOKEN_NAME}
ENV GITEA_TOKEN ${GITEA_TOKEN}

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config http-basic.gitea ${GITEA_TOKEN_NAME} ${GITEA_TOKEN}

RUN poetry install --no-root

COPY . .

CMD /app/docker-entrypoint.sh
