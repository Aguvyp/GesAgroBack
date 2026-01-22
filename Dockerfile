
# Usar una imagen base oficial de Python
FROM python:3.10-slim

# Establecer variables de entorno
# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Evita que Python almacene en búfer stdout y stderr
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
# - default-libmysqlclient-dev, pkg-config, gcc: Para mysqlclient
# - ffmpeg: Para openai-whisper y ffmpeg-python
# - git: A veces necesario para instalar paquetes desde git
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . .

# Copiar el script de entrada y darle permisos de ejecución
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Exponer el puerto que usará Django (por defecto 8000)
EXPOSE 8000

# Usar el script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
