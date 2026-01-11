"""
Servicio de transcripción de audio usando Whisper local.
Procesa archivos de audio de WhatsApp y los transcribe a texto en español.
"""
import os
import tempfile
import requests
import whisper
from typing import Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Modelo Whisper a usar (base es más rápido, small es más preciso)
WHISPER_MODEL_NAME = getattr(settings, 'WHISPER_MODEL', 'base')

# Cache del modelo para no cargarlo múltiples veces
_whisper_model = None


def get_whisper_model():
    """
    Obtiene el modelo Whisper, cargándolo solo una vez.
    
    Returns:
        Modelo Whisper cargado
    """
    global _whisper_model
    if _whisper_model is None:
        logger.info(f"Cargando modelo Whisper: {WHISPER_MODEL_NAME}")
        _whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
        logger.info("Modelo Whisper cargado exitosamente")
    return _whisper_model


def download_audio(url: str, timeout: int = 30) -> Optional[str]:
    """
    Descarga un archivo de audio desde una URL.
    
    Args:
        url: URL del archivo de audio
        timeout: Timeout en segundos para la descarga
        
    Returns:
        Ruta al archivo descargado o None si falla
    """
    try:
        # Crear directorio temporal si no existe
        temp_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Descargar archivo
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.ogg',
            dir=temp_dir
        )
        
        # Escribir contenido
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        
        temp_file.close()
        logger.info(f"Audio descargado: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Error descargando audio: {str(e)}")
        return None


def transcribe_audio(audio_path: str, language: str = 'es') -> Optional[str]:
    """
    Transcribe un archivo de audio a texto usando Whisper.
    
    Args:
        audio_path: Ruta al archivo de audio
        language: Idioma del audio (default: 'es' para español)
        
    Returns:
        Texto transcrito o None si falla
    """
    try:
        if not os.path.exists(audio_path):
            logger.error(f"Archivo de audio no encontrado: {audio_path}")
            return None
        
        # Cargar modelo
        model = get_whisper_model()
        
        # Transcribir
        logger.info(f"Transcribiendo audio: {audio_path}")
        result = model.transcribe(audio_path, language=language)
        
        # Extraer texto
        text = result.get('text', '').strip()
        
        logger.info(f"Transcripción completada: {text[:50]}...")
        return text
        
    except Exception as e:
        logger.error(f"Error transcribiendo audio: {str(e)}")
        return None
    finally:
        # Limpiar archivo temporal
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"Archivo temporal eliminado: {audio_path}")
        except Exception as e:
            logger.warning(f"Error eliminando archivo temporal: {str(e)}")


def transcribe_from_url(audio_url: str, language: str = 'es') -> Optional[str]:
    """
    Descarga y transcribe un audio desde una URL.
    
    Args:
        audio_url: URL del archivo de audio
        language: Idioma del audio (default: 'es')
        
    Returns:
        Texto transcrito o None si falla
    """
    # Descargar audio
    audio_path = download_audio(audio_url)
    if not audio_path:
        return None
    
    # Transcribir
    return transcribe_audio(audio_path, language)


def cleanup_temp_files():
    """
    Limpia archivos temporales antiguos del directorio de temp.
    """
    try:
        temp_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
        if not os.path.exists(temp_dir):
            return
        
        import time
        current_time = time.time()
        max_age = 3600  # 1 hora
        
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age:
                    try:
                        os.remove(file_path)
                        logger.info(f"Archivo temporal antiguo eliminado: {file_path}")
                    except Exception as e:
                        logger.warning(f"Error eliminando archivo: {str(e)}")
    except Exception as e:
        logger.warning(f"Error limpiando archivos temporales: {str(e)}")
