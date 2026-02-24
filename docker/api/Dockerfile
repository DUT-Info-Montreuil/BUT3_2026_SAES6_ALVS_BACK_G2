# docker/api/Dockerfile
# ================================
# Stage 1: Base
# ================================
FROM python:3.12-slim AS base

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ================================
# Stage 2: Development
# ================================
FROM base AS development

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

ENV FLASK_APP=src.infrastructure.web.app:create_app
ENV FLASK_ENV=development

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

# ================================
# Stage 3: Production
# ================================
FROM base AS production

# Créer un utilisateur non-root
RUN useradd -m -u 1000 alvs
USER alvs

COPY --chown=alvs:alvs . .

ENV FLASK_APP=src.infrastructure.web.app:create_app
ENV FLASK_ENV=production

EXPOSE 5000

# Gunicorn pour production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.infrastructure.web.app:create_app()"]
