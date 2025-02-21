FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"
ENV DB_PATH=/app/src/db/main.db
RUN apt-get update

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
    

RUN mkdir -p src/db src/logs

VOLUME /app/src/db
VOLUME /app/src/logs

CMD /bin/bash -c '\
  if [ ! -f $DB_PATH ]; then \
    echo "Database not found, creating..." && \
    uv run src/migrations/create.py; \
  else \
    echo "Database already exists, skipping."; \
  fi'


ENTRYPOINT ["uv", "run", "src/__main__.py"]
