FROM ghcr.io/astral-sh/uv:python3.12-alpine
WORKDIR /app
ADD . /app

RUN uv sync --frozen
EXPOSE 8000
CMD ["sleep", "infinity"]
#CMD ["uv", "run", "fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]