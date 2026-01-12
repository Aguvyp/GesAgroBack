"""
Servicio de transcripción de audio usando la API de OpenAI (Whisper).
Procesa archivos de audio de WhatsApp y los transcribe a texto en español.
No requiere ffmpeg local, usa la API de OpenAI.
"""
import os
import tempfile
import uuid
import time
import requests
import openai
from typing import Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Configuración de OpenAI
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', '')
OPENAI_MODEL = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')


def check_openai_config():
    """
    Verifica si la configuración de OpenAI está disponible.
    
    Returns:
        True si OpenAI está configurado, False en caso contrario
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY no está configurada")
        return False
    logger.info("Configuración de OpenAI disponible")
    return True


def download_audio(url: str, timeout: int = 30) -> Optional[str]:
    """
    Descarga un archivo de audio desde una URL.
    Si la URL es de Twilio, usa autenticación HTTP Basic.
    
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
        
        # Preparar headers y auth
        headers = {}
        auth = None
        
        # Si es una URL de Twilio, usar autenticación
        if 'api.twilio.com' in url:
            twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            
            if twilio_account_sid and twilio_auth_token:
                # HTTP Basic Auth para Twilio
                auth = (twilio_account_sid, twilio_auth_token)
                logger.info("Usando autenticación Twilio para descargar audio")
            else:
                logger.warning("Credenciales de Twilio no encontradas, intentando sin autenticación")
        
        # Descargar archivo
        response = requests.get(url, timeout=timeout, stream=True, auth=auth, headers=headers)
        response.raise_for_status()
        
        # Crear archivo temporal con nombre más simple (evitar caracteres especiales)
        temp_filename = f"audio_{uuid.uuid4().hex[:8]}.ogg"
        file_path = os.path.join(temp_dir, temp_filename)
        
        # Escribir contenido directamente al archivo
        with open(file_path, 'wb') as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filtrar chunks vacíos
                    temp_file.write(chunk)
            # Asegurar que todo se escriba al disco
            temp_file.flush()
            os.fsync(temp_file.fileno())
        
        # Verificar que el archivo se creó correctamente
        file_path = os.path.abspath(file_path)
        file_path = os.path.normpath(file_path)  # Normalizar ruta (compatible Windows/Linux)
        
        if not os.path.exists(file_path):
            logger.error(f"El archivo no se creó correctamente: {file_path}")
            return None
        
        file_size = os.path.getsize(file_path)
        logger.info(f"Audio descargado: {file_path} (tamaño: {file_size} bytes)")
        return file_path
        
    except Exception as e:
        logger.error(f"Error descargando audio: {str(e)}")
        return None


def transcribe_audio(audio_path: str, language: str = 'es') -> Optional[str]:
    """
    Transcribe un archivo de audio a texto usando la API de OpenAI (Whisper).
    No requiere ffmpeg local.
    
    Args:
        audio_path: Ruta al archivo de audio
        language: Idioma del audio (default: 'es' para español)
        
    Returns:
        Texto transcrito o None si falla
    """
    # Verificar configuración de OpenAI
    if not check_openai_config():
        logger.error("No se puede transcribir: OpenAI no está configurado")
        return None
    
    # Convertir a ruta absoluta y normalizar (compatible Windows/Linux)
    audio_path = os.path.abspath(audio_path)
    audio_path = os.path.normpath(audio_path)
    
    transcription_successful = False
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(audio_path):
            logger.error(f"Archivo de audio no encontrado: {audio_path}")
            return None
        
        # Verificar que el archivo no esté vacío
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            logger.error(f"Archivo de audio está vacío: {audio_path}")
            return None
        
        logger.info(f"Archivo encontrado: {audio_path} (tamaño: {file_size} bytes)")
        
        # Verificar que el archivo es accesible
        try:
            with open(audio_path, 'rb') as test_file:
                test_file.read(1)  # Leer un byte para verificar acceso
            logger.info("Archivo es accesible para lectura")
        except Exception as e:
            logger.error(f"No se puede acceder al archivo: {str(e)}")
            return None
        
        # Transcribir usando la API de OpenAI
        logger.info(f"Transcribiendo audio con OpenAI Whisper API: {audio_path}")
        
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Abrir el archivo y enviarlo a OpenAI
            with open(audio_path, 'rb') as audio_file:
                logger.info("Enviando archivo a OpenAI Whisper API...")
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
                
                text = transcript.text.strip()
                transcription_successful = True
                
                if text:
                    logger.info(f"Transcripción completada: {text[:100]}...")
                else:
                    logger.warning("Transcripción completada pero el texto está vacío")
                
                return text
                
        except openai.APIError as e:
            logger.error(f"Error de API de OpenAI: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error durante transcripción con OpenAI: {str(e)}", exc_info=True)
            return None
        
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado durante transcripción: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error transcribiendo audio: {str(e)}", exc_info=True)
        return None
    finally:
        # Limpiar archivo temporal SOLO si la transcripción fue exitosa
        if transcription_successful:
            try:
                time.sleep(0.2)  # Pequeño delay para asegurar que el archivo no esté en uso
                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        logger.info(f"Archivo temporal eliminado: {audio_path}")
                    except PermissionError:
                        logger.warning(f"No se pudo eliminar archivo (puede estar en uso): {audio_path}")
                        # Intentar de nuevo después de un delay
                        time.sleep(1)
                        try:
                            os.remove(audio_path)
                            logger.info(f"Archivo temporal eliminado (segundo intento): {audio_path}")
                        except Exception as e2:
                            logger.warning(f"Error eliminando archivo temporal: {str(e2)}")
            except Exception as e:
                logger.warning(f"Error limpiando archivo temporal: {str(e)}")
        else:
            logger.warning("Transcripción falló, manteniendo archivo para debugging")
            logger.warning(f"Archivo: {audio_path if 'audio_path' in locals() else 'N/A'}")


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
