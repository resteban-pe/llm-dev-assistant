FROM python:3.11-slim

WORKDIR /app

# usuario no-root (antes del código para permisos correctos)
RUN adduser --disabled-password --gecos "" --home /app appuser

# layer cache: dependencias primero
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# código fuente
COPY app/ ./app/
COPY prompts/ ./prompts/

USER appuser

EXPOSE 8083

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"]
