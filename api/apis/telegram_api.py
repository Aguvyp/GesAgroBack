"""Endpoint que recibe actualizaciones de Telegram y lanza OpenCode."""
import logging
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..services.telegram_agent import process_telegram_message

logger = logging.getLogger(__name__)


def _send_telegram_message(chat_id: int, text: str) -> bool:
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        logger.error('TELEGRAM_BOT_TOKEN no está configurado. No se puede enviar respuesta.')
        return False

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.error('Error enviando mensaje a Telegram: %s', exc)
        return False


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_webhook(request):
    update = request.data if isinstance(request.data, dict) else {}
    message = update.get('message') or update.get('edited_message')

    if not message:
        return Response({'status': 'ignored'}, status=status.HTTP_200_OK)

    chat = message.get('chat', {})
    chat_id = chat.get('id')
    text = message.get('text')
    contact = message.get('contact')
    contact_phone = contact.get('phone_number') if contact else None

    if not chat_id:
        return Response({'error': 'No se encontró chat_id'}, status=status.HTTP_400_BAD_REQUEST)

    result = process_telegram_message(chat_id, text, contact_phone)
    reply = result.get('reply', 'Estoy procesando tu solicitud.')

    sent = _send_telegram_message(chat_id, reply)
    status_code = status.HTTP_200_OK if sent else status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response({'success': sent, 'reply': reply}, status=status_code)
