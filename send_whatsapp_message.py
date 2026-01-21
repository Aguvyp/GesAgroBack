"""
Script simple para enviar un mensaje único al webhook de WhatsApp.
Útil para pruebas rápidas o integración en scripts.

Uso:
    python send_whatsapp_message.py "Tu mensaje aquí"
    python send_whatsapp_message.py "Listar mis campos" --phone +5491112345678
"""

import os
import sys
import django
import argparse
from unittest.mock import patch
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from api.apis.whatsapp_api import whatsapp_webhook
from api.services.whatsapp_auth import normalize_phone_number

User = get_user_model()


# Mock classes para Twilio
class MockTwilioMessage:
    """Mock de un mensaje de Twilio"""
    def __init__(self, body, from_, to):
        self.sid = f'SM{datetime.now().strftime("%Y%m%d%H%M%S%f")}'
        self.body = body
        self.from_ = from_
        self.to = to
        self.status = 'sent'


class MockTwilioMessages:
    """Mock del gestor de mensajes de Twilio"""
    def create(self, body, from_, to):
        return MockTwilioMessage(body, from_, to)


class MockTwilioClient:
    """Mock del cliente de Twilio"""
    def __init__(self, account_sid, auth_token):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.messages = MockTwilioMessages()


def get_default_phone():
    """Obtiene el primer usuario con teléfono configurado"""
    user = User.objects.exclude(telefono__isnull=True).exclude(telefono='').first()
    if user:
        return normalize_phone_number(user.telefono)
    return None


def send_message(message_text: str, from_phone: str):
    """
    Envía un mensaje al webhook simulando Twilio.
    
    Args:
        message_text: Texto del mensaje
        from_phone: Número de teléfono del remitente
    
    Returns:
        Tuple (success, response_message, twilio_message_body)
    """
    factory = RequestFactory()
    
    # Datos que envía Twilio
    twilio_data = {
        'MessageSid': f'SM{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'AccountSid': 'AC_TEST_SIMULATOR',
        'MessagingServiceSid': 'MG_TEST',
        'From': f'whatsapp:{from_phone}',
        'To': 'whatsapp:+14155238886',
        'Body': message_text,
        'NumMedia': '0',
    }
    
    # Crear request POST
    request = factory.post(
        '/api/whatsapp/webhook/',
        data=twilio_data,
        content_type='application/x-www-form-urlencoded'
    )
    
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
    
    # Variable para capturar la respuesta de Twilio
    twilio_response_body = None
    
    # Mock personalizado que captura el body
    class CaptureBodyMockMessage:
        def __init__(self, body, from_, to):
            nonlocal twilio_response_body
            self.sid = f'SM{datetime.now().strftime("%Y%m%d%H%M%S%f")}'
            self.body = body
            self.from_ = from_
            self.to = to
            self.status = 'sent'
            twilio_response_body = body
    
    class CaptureBodyMockMessages:
        def create(self, body, from_, to):
            return CaptureBodyMockMessage(body, from_, to)
    
    class CaptureBodyMockClient:
        def __init__(self, account_sid, auth_token):
            self.account_sid = account_sid
            self.auth_token = auth_token
            self.messages = CaptureBodyMockMessages()
    
    # Llamar al webhook con mock de Twilio
    with patch('api.apis.whatsapp_api.Client', CaptureBodyMockClient):
        response = whatsapp_webhook(request)
    
    if response.status_code == 200:
        response_data = response.data
        return response_data.get('success', False), response_data.get('message', 'Sin respuesta'), twilio_response_body
    else:
        error_data = response.data if hasattr(response, 'data') else {}
        return False, error_data.get('error', f'HTTP {response.status_code}'), None


def main():
    parser = argparse.ArgumentParser(
        description='Envía un mensaje al webhook de WhatsApp para pruebas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python send_whatsapp_message.py "Listar mis campos"
  python send_whatsapp_message.py "Crear campo La Esperanza" --phone +5491112345678
  python send_whatsapp_message.py "Mostrar reporte de hoy" -p +5491112345678
        """
    )
    
    parser.add_argument(
        'message',
        type=str,
        help='Mensaje a enviar'
    )
    
    parser.add_argument(
        '-p', '--phone',
        type=str,
        default=None,
        help='Número de teléfono del remitente (formato: +54...). Si no se especifica, usa el primer usuario con teléfono.'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    args = parser.parse_args()
    
    # Obtener teléfono
    phone = args.phone
    if not phone:
        phone = get_default_phone()
        if not phone:
            print("❌ Error: No hay usuarios con teléfono configurado.")
            print("   Usa --phone para especificar un número o configura un usuario con teléfono.")
            return 1
        if args.verbose:
            print(f"ℹ️  Usando teléfono por defecto: {phone}")
    
    # Enviar mensaje
    if args.verbose:
        print(f"📤 Enviando mensaje desde {phone}...")
        print(f"💬 Mensaje: {args.message}")
        print()
    
    try:
        success, response, twilio_body = send_message(args.message, phone)
        
        if success:
            print(f"✅ Éxito")
            if twilio_body:
                print(f"🤖 Respuesta (enviada a Twilio): {twilio_body}")
            else:
                print(f"🤖 Respuesta: {response}")
            return 0
        else:
            print(f"❌ Error")
            print(f"📝 Mensaje: {response}")
            return 1
    
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
