FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn==23.0.0
COPY . .
# Disable any preexisting env that could point gunicorn to app.wsgi
ENV GUNICORN_CMD_ARGS=""
# Explicit gunicorn command targeting main:app
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "main:app"]
