# Guía de Configuración Docker para GesAgroBack

Este proyecto ha sido dockerizado para facilitar el desarrollo y despliegue.

## Requisitos Previos

- Docker
- Docker Compose

## Estructura de Servicios

El archivo `docker-compose.yml` define los siguientes servicios:
1.  **web**: La aplicación Django. Se ejecuta en el puerto `8000`.
2.  **db**: Base de datos MySQL 8.0. Expuesta en el puerto `3307` del host (para evitar conflictos con MySQL local).
3.  **phpmyadmin**: Interfaz web para gestionar la base de datos. Se ejecuta en el puerto `8080`.

## Instrucciones de Uso

### 1. Construir e Iniciar los Servicio

Para iniciar todos los servicios, ejecuta:

```bash
docker-compose up --build
```

Esto construirá la imagen de Docker para la aplicación (instalando dependencias como `ffmpeg` y `mysqlclient`) e iniciará la base de datos.
La primera vez puede tardar unos minutos en descargar las imágenes e instalar las dependencias.

### 2. Acceso

- **API/Web**: [http://localhost:8000](http://localhost:8000)
- **PhpMyAdmin**: [http://localhost:8080](http://localhost:8080) (Usuario: `root`, Contraseña: `root`)
- **Base de Datos (Directo)**: `localhost:3307`

### 3. Migraciones y Comandos de Gestión

El contenedor `web` ejecuta automáticamente las migraciones al iniciar (gracias al script `entrypoint.sh`).

Si necesitas ejecutar comandos administrativos (como crear un superusuario), puedes hacerlo dentro del contenedor en ejecución:

```bash
# Crear un superusuario
docker-compose exec web python manage.py createsuperuser

# Crear nuevas migraciones (si modificas modelos)
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 4. Variables de Entorno

El servicio utiliza el archivo `.env` si existe. Asegúrate de configurar tus claves de API (OpenAI, Twilio) en él.
La configuración de la base de datos en `docker-compose.yml` sobrescribe la del archivo `.env` para asegurar que la conexión interna entre contenedores funcione correctamente.

## Solución de Problemas

- **Error de conexión a BD**: Si la aplicación web falla al inicio diciendo que no puede conectar a la base de datos, es normal en el primer arranque mientras MySQL se inicializa. El contenedor se reiniciará automáticamente hasta que la BD esté lista.
- **Cambios en requirements.txt**: Si agregas nuevas dependencias, debes reconstruir la imagen:
  ```bash
  docker-compose up --build
  ```
