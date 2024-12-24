# Dockerfile
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY main.py .

# Exponer puerto
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]

# requirements.txt
