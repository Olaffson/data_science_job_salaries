# Utiliser une image de base officielle de Python
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances de l'API
COPY api/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l'API et le modèle
COPY api/ ./api/

# Exposer le port sur lequel l'application va s'exécuter
EXPOSE 8000

# Lancer l'application FastAPI avec uvicorn
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
