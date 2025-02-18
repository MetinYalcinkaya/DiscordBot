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

# need to create db, otherwire returns None
# RUN ["python", "src/migrations/create.py"]
# RUN uv run src/migrations/create.py
RUN ["uv", "run", "src/migrations/create.py"]

ENTRYPOINT ["uv", "run", "src/__main__.py"]
