FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

RUN apt-get update

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
    
ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir -p src/db src/logs

VOLUME /app/src/db
VOLUME /app/src/logs

RUN if [ ! -f src/db/main.db ]; then \
    uv run src/migrations/create.py; \
fi

ENTRYPOINT ["uv", "run", "src/__main__.py"]
