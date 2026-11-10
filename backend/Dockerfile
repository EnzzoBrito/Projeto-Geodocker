FROM python:3.11-slim

LABEL maintainer="Hermes Tupinamba, Carlos Garcia, Enzo Brito"
LABEL description="GeoDocker Challenge Backend REST API"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app

# Instala dependências do sistema necessárias para compilação do psycopg2 e curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Cache de dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY app /app/app

EXPOSE 5000

# Executa o servidor FastAPI com Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
