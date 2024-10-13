# Utiliser une image de base Python 3.9
FROM python:3.9

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source dans l'image
COPY . .

# Exposer les ports 8000 pour FastAPI et 8501 pour Streamlit
EXPOSE 8000
EXPOSE 8501

# Commande pour lancer FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Commande pour lancer Streamlit en mode production
CMD ["streamlit", "run", "interface.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
