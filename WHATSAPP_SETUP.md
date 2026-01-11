# Configuración de WhatsApp con Twilio

## Requisitos Previos

1. **Cuenta de Twilio** con WhatsApp habilitado
2. **FFmpeg instalado** en el sistema (requerido por Whisper)
3. **Python 3.8+** con las dependencias instaladas

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Instalar FFmpeg

**Windows:**
- Descargar desde https://ffmpeg.org/download.html
- Agregar al PATH del sistema

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. Configurar variables de entorno

Copiar `env.example` a `.env` y completar:

```bash
cp env.example .env
```

Editar `.env` con tus credenciales de Twilio:

```
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
WHISPER_MODEL=base
```

### 4. Configurar webhook en Twilio

1. Ir a la consola de Twilio → WhatsApp → Sandbox (o tu número aprobado)
2. Configurar webhook URL: `https://tu-dominio.com/api/whatsapp/webhook/`
3. Método: POST

**Para desarrollo local:**
- Usar ngrok: `ngrok http 8000`
- Configurar webhook: `https://tu-url-ngrok.ngrok-free.app/api/whatsapp/webhook/`

### 5. Configurar números de teléfono autorizados

Los usuarios deben tener su número de teléfono en el campo `telefono` de la tabla `personal` o `clientes`.

El formato debe ser: `+5491123456789` (con código de país y sin espacios).

## Uso

### Mensajes de Texto

Los usuarios pueden enviar mensajes como:

- "Crear trabajo de siembra de soja en campo Norte, fecha inicio 15/03/2024"
- "Crear costo de 50000 pesos para combustible, fecha hoy"
- "Crear campo llamado Sur"
- "Crear cliente llamado Juan Pérez"

### Mensajes de Audio

Los usuarios pueden enviar audios de voz que serán transcritos automáticamente y procesados igual que mensajes de texto.

## Modelos

### Whisper

El modelo por defecto es `base` (balance velocidad/precisión). Opciones:
- `tiny`: Más rápido, menos preciso
- `base`: Balance (recomendado)
- `small`: Más preciso, más lento
- `medium`: Muy preciso, lento
- `large`: Máxima precisión, muy lento

Cambiar en `.env`: `WHISPER_MODEL=small`

### Sentence Transformers

El modelo de embeddings se descarga automáticamente la primera vez (~80MB):
- `paraphrase-multilingual-MiniLM-L12-v2`

## Solución de Problemas

### Error: "FFmpeg not found"
- Verificar que FFmpeg está instalado y en el PATH
- Reiniciar el servidor después de instalar FFmpeg

### Error: "Model not found"
- Los modelos se descargan automáticamente la primera vez
- Verificar conexión a internet
- Verificar espacio en disco (modelos ocupan ~150-500MB)

### Error: "No estás autorizado"
- Verificar que el número de teléfono está en la base de datos
- Formato correcto: `+5491123456789`
- Verificar que el usuario está activo

### Audio no se transcribe
- Verificar que el audio es compatible (OGG, MP3, WAV)
- Verificar tamaño del audio (máximo recomendado: 10MB)
- Verificar logs para más detalles

## Logs

Los logs se guardan en el logger de Django. Para ver logs en desarrollo:

```python
# En settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api.services': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```
