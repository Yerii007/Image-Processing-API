FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid 1001 --home /app --shell /bin/bash appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

RUN mkdir -p /app/uploads/originals /app/uploads/processed /app/logs

EXPOSE 5000

CMD ["python", "app.py"]


