FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
ADD . /app


RUN uv sync --frozen

CMD ["uv", "run", "main.py"]
