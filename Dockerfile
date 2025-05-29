FROM ghcr.io/astral-sh/uv:debian
WORKDIR /app
ADD . /app

RUN uv sync --frozen
EXPOSE 8000
CMD ["uv", "run", "fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]