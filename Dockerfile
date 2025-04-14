FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
RUN uv sync --frozen

# Comando de execução
CMD ["uv", "run", "main.py"]
