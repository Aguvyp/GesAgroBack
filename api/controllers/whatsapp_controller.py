"""
Controlador principal para procesar mensajes de WhatsApp.
Orquesta todo el flujo: detección de tipo, transcripción, procesamiento con OpenAI.
"""
from typing import Dict, Optional, Tuple
import logging
from ..services.whatsapp_auth import is_authorized_phone, normalize_phone_number, get_user_by_phone
from ..services.whatsapp_audio_transcriber import transcribe_from_url, cleanup_temp_files
from ..services.whatsapp_openai_agent import process_with_openai

logger = logging.getLogger(__name__)


def process_whatsapp_message(
    phone: str,
    message_text: Optional[str] = None,
    audio_url: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Procesa un mensaje de WhatsApp (texto o audio) usando OpenAI con function calling.
    Soporta operaciones CRUD completas (Crear, Leer, Actualizar, Eliminar).
    
    Args:
        phone: Número de teléfono del remitente
        message_text: Texto del mensaje (si es mensaje de texto)
        audio_url: URL del audio (si es mensaje de audio)
        
    Returns:
        Tupla (éxito, mensaje_respuesta)
    """
    try:
        logger.info("\n" + "=" * 80)
        logger.info("🚀 INICIANDO PROCESAMIENTO DE MENSAJE")
        logger.info("=" * 80)
        
        # 1. Validar autorización
        logger.info("📋 PASO 1: Validando autorización...")
        logger.info(f"   Teléfono: {phone}")
        if not is_authorized_phone(phone):
            logger.error("   ❌ Teléfono NO autorizado")
            return False, "❌ No estás autorizado para usar este servicio. Contacta al administrador."
        logger.info("   ✅ Teléfono autorizado")
        
        # 1.5. Obtener usuario
        logger.info("\n📋 PASO 1.5: Obteniendo usuario...")
        user = get_user_by_phone(phone)
        if not user:
            logger.error("   ❌ No se pudo obtener el usuario")
            return False, "❌ Error: No se pudo identificar tu usuario. Contacta al administrador."
        logger.info(f"   ✅ Usuario identificado: {user.email} (ID: {user.id})")
        
        # 2. Obtener texto del mensaje (transcribir si es audio)
        logger.info("\n📋 PASO 2: Obteniendo texto del mensaje...")
        text = None
        is_from_audio = False
        
        if audio_url:
            logger.info(f"   🔊 Procesando mensaje de audio desde {phone}")
            logger.info(f"   URL del audio: {audio_url}")
            text = transcribe_from_url(audio_url, language='es')
            is_from_audio = True
            if not text:
                logger.error("   ❌ Error transcribiendo audio")
                # Verificar si es un problema de ffmpeg
                from ..services.whatsapp_audio_transcriber import check_ffmpeg
                if not check_ffmpeg():
                    return False, "❌ No puedo transcribir audio porque ffmpeg no está instalado en el servidor. Por favor, contacta al administrador o envía un mensaje de texto."
                return False, "❌ No pude transcribir el audio. Por favor, intenta enviar un mensaje de texto."
            logger.info(f"   ✅ Audio transcrito: {text[:100]}...")
        elif message_text:
            text = message_text
            logger.info(f"   ✅ Mensaje de texto recibido: {text[:100]}...")
        else:
            logger.error("   ❌ No se recibió ningún mensaje")
            return False, "❌ No se recibió ningún mensaje."
        
        # 3. Procesar con OpenAI
        logger.info("\n📋 PASO 3: Procesando con OpenAI...")
        logger.info(f"   Texto: {text}")
        
        success, response_message = process_with_openai(text, usuario_id=user.id)
        
        if success:
            if is_from_audio:
                response_message += "\n\n(Procesado desde audio)"
            logger.info("\n" + "=" * 80)
            logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
            logger.info("=" * 80 + "\n")
            return True, response_message
        else:
            logger.error("\n" + "=" * 80)
            logger.error("❌ PROCESO FALLÓ")
            logger.error("=" * 80 + "\n")
            return False, response_message
    
    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error("❌ ERROR EXCEPCIONAL EN EL PROCESAMIENTO")
        logger.error(f"   Error: {str(e)}")
        logger.error("=" * 80 + "\n")
        logger.error("Traceback completo:", exc_info=True)
        return False, f"❌ Error interno: {str(e)}"
    finally:
        # Limpiar archivos temporales
        logger.debug("🧹 Limpiando archivos temporales...")
        cleanup_temp_files()
