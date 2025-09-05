# Dockerfile
# Basis-Image für Python
FROM python:3.10-slim

# Arbeitsverzeichnis im Container setzen
WORKDIR /app

# requirements.txt kopieren und Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den gesamten Quellcode kopieren
COPY . .

# Standardbefehl, der beim Start des Containers ausgeführt wird
# Zeigt die Hilfe an, wenn kein anderer Befehl angegeben wird.
ENTRYPOINT ["python", "-m", "sinister_snare.cli"]
CMD ["--help"]