FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md .
COPY src ./src
COPY scripts ./scripts

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "tg_bot.main"]
