FROM python:3.12-slim

WORKDIR /app

# Copie les dépendances et installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie l'application
COPY app.py .

# Exposition du port Streamlit
EXPOSE 8501

# Commande de démarrage avec baseUrlPath
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.baseUrlPath=/jimpe"]