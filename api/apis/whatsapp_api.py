"""
API endpoint para el webhook de Twilio WhatsApp.
Recibe mensajes de texto y audio desde Twilio y los procesa.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from twilio.request_validator import RequestValidator
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging
from ..controllers.whatsapp_controller import process_whatsapp_message
from twilio.rest import Client

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    """
    Webhook endpoint para recibir mensajes de WhatsApp desde Twilio.
    
    Valida la firma de Twilio, extrae el mensaje/audio y lo procesa.
    Responde con un mensaje de texto a WhatsApp.
    """
    try:
        # Validar firma de Twilio (solo en producción)
        twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        validate_signature = getattr(settings, 'TWILIO_VALIDATE_SIGNATURE', True)
        
        if twilio_auth_token and validate_signature:
            try:
                validator = RequestValidator(twilio_auth_token)
                signature = request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
                
                # Obtener la URL completa del request
                # Si hay un header X-Forwarded-Proto o X-Forwarded-Host, usarlo
                url = request.build_absolute_uri()
                
                # Si estamos detrás de un proxy (ngrok), usar la URL original
                forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST', '')
                forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO', '')
                
                if forwarded_host:
                    if forwarded_proto:
                        url = f"{forwarded_proto}://{forwarded_host}{request.path}"
                    else:
                        url = f"https://{forwarded_host}{request.path}"
                
                # Obtener datos del POST
                post_data = request.POST if hasattr(request, 'POST') and request.POST else {}
                
                # Si no hay datos en POST, intentar obtener del body
                if not post_data and request.body:
                    import urllib.parse
                    body_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
                    # Convertir a formato que espera el validador
                    post_data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v 
                                for k, v in body_data.items()}
                
                if not validator.validate(url, post_data, signature):
                    logger.warning(f"Firma de Twilio inválida. URL: {url}, Signature presente: {bool(signature)}")
                    # En desarrollo, solo loguear el warning pero continuar
                    if settings.DEBUG:
                        logger.warning("Modo DEBUG: Continuando sin validar firma")
                    else:
                        return Response({'error': 'Invalid signature'}, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                logger.error(f"Error validando firma de Twilio: {str(e)}")
                # En desarrollo, continuar aunque falle la validación
                if not settings.DEBUG:
                    return Response({'error': 'Signature validation error'}, status=status.HTTP_403_FORBIDDEN)
        
        # Extraer datos del request
        # Intentar obtener de POST primero, luego del body
        if hasattr(request, 'POST') and request.POST:
            from_number = request.POST.get('From', '').replace('whatsapp:', '')
            message_body = request.POST.get('Body', '')
            num_media = int(request.POST.get('NumMedia', 0))
        else:
            # Si no hay POST, parsear del body
            import urllib.parse
            body_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
            from_number = body_data.get('From', [''])[0].replace('whatsapp:', '')
            message_body = body_data.get('Body', [''])[0]
            num_media = int(body_data.get('NumMedia', ['0'])[0])
        
        # Determinar si es audio o texto (inicializar antes de usar en logging)
        audio_url = None
        if num_media > 0:
            # Twilio envía MediaContentType0, MediaUrl0, etc.
            if hasattr(request, 'POST') and request.POST:
                media_type = request.POST.get('MediaContentType0', '')
                audio_url = request.POST.get('MediaUrl0', '')
            else:
                import urllib.parse
                body_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
                media_type = body_data.get('MediaContentType0', [''])[0]
                audio_url = body_data.get('MediaUrl0', [''])[0]
            
            if 'audio' in media_type.lower() or 'ogg' in media_type.lower():
                logger.info(f"Audio detectado: {audio_url}")
            else:
                # Si hay media pero no es audio, resetear audio_url
                audio_url = None
        
        # Logging del mensaje recibido (después de determinar tipo)
        logger.info("=" * 80)
        logger.info("📱 MENSAJE DE WHATSAPP RECIBIDO")
        logger.info(f"   Desde: {from_number}")
        logger.info(f"   Tipo: {'Audio' if audio_url else 'Texto'}")
        logger.info(f"   Cuerpo: {message_body[:100] if message_body else 'N/A'}...")
        logger.info(f"   NumMedia: {num_media}")
        if audio_url:
            logger.info(f"   URL Audio: {audio_url}")
        logger.info("=" * 80)
        
        # Procesar mensaje
        success, response_message = process_whatsapp_message(
            phone=from_number,
            message_text=message_body if not audio_url else None,
            audio_url=audio_url
        )
        
        # Enviar respuesta a WhatsApp usando Twilio
        twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        twilio_whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
        
        # Validar que las credenciales estén configuradas
        if not twilio_account_sid or not twilio_auth_token or not twilio_whatsapp_number:
            logger.error(f"Credenciales de Twilio no configuradas. SID: {bool(twilio_account_sid)}, Token: {bool(twilio_auth_token)}, Number: {bool(twilio_whatsapp_number)}")
        elif twilio_account_sid == 'your_twilio_account_sid_here' or twilio_auth_token == 'your_twilio_auth_token_here':
            logger.error("Credenciales de Twilio aún tienen valores de ejemplo. Por favor configura el archivo .env")
        else:
            try:
                # Limpiar credenciales de espacios
                twilio_account_sid = twilio_account_sid.strip()
                twilio_auth_token = twilio_auth_token.strip()
                twilio_whatsapp_number = twilio_whatsapp_number.strip()
                
                logger.info(f"Enviando mensaje a {from_number} desde {twilio_whatsapp_number}")
                client = Client(twilio_account_sid, twilio_auth_token)
                
                message = client.messages.create(
                    body=response_message,
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    to=f'whatsapp:{from_number}'
                )
                logger.info(f"Respuesta enviada exitosamente. Message SID: {message.sid}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error enviando respuesta vía Twilio: {error_msg}")
                
                # Proporcionar mensajes de error más específicos
                if 'Authentication Error' in error_msg or 'invalid username' in error_msg.lower():
                    logger.error("ERROR DE AUTENTICACIÓN: Verifica que TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN en .env sean correctos")
                    logger.error(f"Account SID configurado: {twilio_account_sid[:10]}... (longitud: {len(twilio_account_sid)})")
                elif 'not found' in error_msg.lower() or 'does not exist' in error_msg.lower():
                    logger.error("ERROR: El número de WhatsApp no existe o no está verificado en Twilio")
                    logger.error(f"Número configurado: {twilio_whatsapp_number}")
                
                # Aún así retornamos éxito al webhook para que Twilio no reintente
        
        # Retornar respuesta TwiML (aunque ya enviamos el mensaje)
        return Response({
            'success': success,
            'message': response_message
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error en webhook de WhatsApp: {str(e)}", exc_info=True)
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
