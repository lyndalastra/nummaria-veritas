FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY data ./data

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "nummaria_veritas.api.app:app", "--host", "0.0.0.0", "--port", "8000"]