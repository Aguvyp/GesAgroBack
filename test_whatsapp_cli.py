"""
Script CLI para simular mensajes de WhatsApp/Twilio y depurar el webhook localmente.

Este script:
- Simula el formato de datos que envía Twilio al webhook
- Mockea el cliente de Twilio para que las respuestas se muestren en consola en lugar de enviarse
- Permite depurar el flujo completo tal como funciona en producción
- La consola actúa como si fuera Twilio recibiendo y enviando mensajes

Uso:
    python test_whatsapp_cli.py
    
    Luego escribe mensajes en la consola y presiona Enter.
    Escribe 'salir' o 'exit' para terminar.
"""

import os
import sys
import django
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from api.apis.whatsapp_api import whatsapp_webhook
from api.services.whatsapp_auth import normalize_phone_number

User = get_user_model()


class Colors:
    """Colores ANSI para la consola"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Variable global para capturar las respuestas de Twilio
last_twilio_response = None


class MockTwilioMessage:
    """Mock de un mensaje de Twilio"""
    def __init__(self, body, from_, to):
        self.sid = f'SM{datetime.now().strftime("%Y%m%d%H%M%S%f")}'
        self.body = body
        self.from_ = from_
        self.to = to
        self.status = 'sent'
        
        # Guardar globalmente para que el CLI lo pueda mostrar
        global last_twilio_response
        last_twilio_response = {
            'body': body,
            'from': from_,
            'to': to,
            'sid': self.sid
        }


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


def print_banner():
    """Imprime el banner de inicio"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("  🤖 SIMULADOR DE WHATSAPP - GEMINI CLI")
    print("=" * 80)
    print(f"{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Este simulador te permite probar el webhook de WhatsApp localmente.")
    print(f"La consola simula ser Twilio: recibe mensajes y muestra las respuestas.{Colors.ENDC}\n")


def get_test_phone():
    """
    Obtiene el número de teléfono de prueba.
    Busca un usuario con teléfono configurado en la base de datos.
    """
    print(f"{Colors.WARNING}Buscando usuarios con teléfono configurado...{Colors.ENDC}")
    
    # Buscar usuarios con teléfono
    users_with_phone = User.objects.exclude(telefono__isnull=True).exclude(telefono='')
    
    if not users_with_phone.exists():
        print(f"{Colors.FAIL}❌ No hay usuarios con teléfono configurado en la base de datos.{Colors.ENDC}")
        print(f"{Colors.WARNING}Por favor, configura un teléfono para un usuario primero.{Colors.ENDC}")
        return None
    
    print(f"\n{Colors.OKGREEN}Usuarios disponibles:{Colors.ENDC}")
    for i, user in enumerate(users_with_phone, 1):
        phone = normalize_phone_number(user.telefono)
        print(f"  {i}. {user.email} - {phone}")
    
    # Si solo hay un usuario, usarlo automáticamente
    if users_with_phone.count() == 1:
        user = users_with_phone.first()
        phone = normalize_phone_number(user.telefono)
        print(f"\n{Colors.OKGREEN}✅ Usando automáticamente: {user.email} ({phone}){Colors.ENDC}")
        return phone
    
    # Si hay múltiples usuarios, pedir selección
    while True:
        try:
            choice = input(f"\n{Colors.OKCYAN}Selecciona un usuario (1-{users_with_phone.count()}): {Colors.ENDC}")
            choice_num = int(choice)
            if 1 <= choice_num <= users_with_phone.count():
                user = list(users_with_phone)[choice_num - 1]
                phone = normalize_phone_number(user.telefono)
                print(f"{Colors.OKGREEN}✅ Seleccionado: {user.email} ({phone}){Colors.ENDC}")
                return phone
            else:
                print(f"{Colors.FAIL}Por favor, selecciona un número válido.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Por favor, ingresa un número.{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Cancelado por el usuario.{Colors.ENDC}")
            return None


def simulate_twilio_request(message_text: str, from_phone: str):
    """
    Simula una petición POST de Twilio al webhook.
    
    Args:
        message_text: El texto del mensaje a enviar
        from_phone: El número de teléfono del remitente (formato: +54...)
    
    Returns:
        Response object del webhook
    """
    global last_twilio_response
    last_twilio_response = None  # Reset
    
    from django.http import QueryDict
    import urllib.parse
    
    factory = RequestFactory()
    
    # Datos que envía Twilio en un mensaje de texto
    twilio_data = {
        'MessageSid': f'SM{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'AccountSid': 'AC_TEST_SIMULATOR',
        'MessagingServiceSid': 'MG_TEST',
        'From': f'whatsapp:{from_phone}',
        'To': 'whatsapp:+14155238886',  # Número de Twilio sandbox
        'Body': message_text,
        'NumMedia': '0',
    }
    
    # Crear el body como lo enviaría Twilio (application/x-www-form-urlencoded)
    body = urllib.parse.urlencode(twilio_data)
    
    # Crear request POST simulado
    request = factory.post(
        '/api/whatsapp/webhook/',
        data=body,
        content_type='application/x-www-form-urlencoded'
    )
    
    # Asegurarse de que request.POST esté poblado correctamente
    # Django parsea automáticamente el body si el content-type es correcto
    # pero por si acaso, lo forzamos
    if not request.POST:
        request._post = QueryDict(body, encoding='utf-8')
    
    # Agregar metadatos que espera el webhook
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
    
    # Patchear el cliente de Twilio para que use nuestro mock
    with patch('api.apis.whatsapp_api.Client', MockTwilioClient):
        # Llamar al webhook
        response = whatsapp_webhook(request)
    
    return response


def print_message(role: str, message: str, metadata: dict = None):
    """Imprime un mensaje formateado"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if role == "user":
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}[{timestamp}] � WhatsApp → Webhook{Colors.ENDC}")
        print(f"{Colors.OKBLUE}👤 Usuario: {message}{Colors.ENDC}")
        
    elif role == "twilio":
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}[{timestamp}] 📤 Webhook → Twilio → WhatsApp{Colors.ENDC}")
        print(f"{Colors.OKGREEN}🤖 Asistente: {message}{Colors.ENDC}")
        if metadata:
            print(f"{Colors.WARNING}   [Message SID: {metadata.get('sid', 'N/A')}]{Colors.ENDC}")
            
    elif role == "system":
        print(f"\n{Colors.WARNING}[{timestamp}] ⚙️  Sistema: {message}{Colors.ENDC}")
        
    elif role == "error":
        print(f"\n{Colors.FAIL}[{timestamp}] ❌ Error: {message}{Colors.ENDC}")


def print_help():
    """Imprime la ayuda"""
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}Ayuda:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  Escribe cualquier mensaje para enviarlo al asistente")
    print(f"  El asistente puede ejecutar funciones (tools) de OpenAI")
    print(f"  Puedes pedir crear, leer, actualizar o eliminar datos{Colors.ENDC}")
    print(f"\n{Colors.OKGREEN}Ejemplos de mensajes:{Colors.ENDC}")
    print(f"  • 'Hola, qué puedes hacer?'")
    print(f"  • 'Listar mis campos'")
    print(f"  • 'Mostrar todas las máquinas'")
    print(f"  • 'Crear un nuevo campo llamado La Esperanza de 100 hectáreas'")
    print(f"  • 'Cuántas horas trabajó la máquina 123 esta semana?'")
    print(f"  • 'Mostrar el reporte de hoy'")
    print(f"\n{Colors.WARNING}Comandos especiales:{Colors.ENDC}")
    print(f"  • 'salir' o 'exit': Terminar la sesión")
    print(f"  • 'clear' o 'cls': Limpiar la pantalla")
    print(f"  • 'help': Mostrar esta ayuda")


def main():
    """Función principal del CLI"""
    print_banner()
    
    # Obtener teléfono de prueba
    test_phone = get_test_phone()
    if not test_phone:
        return
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}=" * 80)
    print("  SESIÓN INICIADA - MODO SIMULACIÓN TWILIO")
    print("=" * 80 + f"{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Escribe tus mensajes y presiona Enter.{Colors.ENDC}")
    print(f"{Colors.OKCYAN}El flujo completo se ejecutará: Webhook → OpenAI → Tools → Twilio (simulado){Colors.ENDC}\n")
    
    # Mostrar ayuda inicial
    print_help()
    
    # Loop principal
    message_count = 0
    while True:
        try:
            # Leer mensaje del usuario
            user_input = input(f"\n{Colors.BOLD}📱 Tú > {Colors.ENDC}").strip()
            
            # Comandos especiales
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print(f"\n{Colors.WARNING}👋 Cerrando sesión...{Colors.ENDC}")
                print(f"{Colors.OKGREEN}Total de mensajes enviados: {message_count}{Colors.ENDC}\n")
                break
            
            if user_input.lower() in ['clear', 'cls']:
                os.system('cls' if os.name == 'nt' else 'clear')
                print_banner()
                continue
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            if not user_input:
                continue
            
            # Mostrar mensaje del usuario (como si Twilio lo enviara al webhook)
            print_message("user", user_input)
            
            # Simular envío a webhook
            print_message("system", "Procesando en webhook... (validando, llamando OpenAI, ejecutando tools...)")
            
            try:
                response = simulate_twilio_request(user_input, test_phone)
                message_count += 1
                
                # Procesar respuesta del webhook
                if response.status_code == 200:
                    response_data = response.data
                    
                    # Mostrar la respuesta que el webhook intentó enviar por Twilio
                    if last_twilio_response:
                        # Esta es la respuesta que se "envió" a Twilio (mockeado)
                        print_message("twilio", last_twilio_response['body'], {
                            'sid': last_twilio_response['sid'],
                            'from': last_twilio_response['from'],
                            'to': last_twilio_response['to']
                        })
                    else:
                        # Si no hubo respuesta de Twilio, mostrar la respuesta del webhook
                        if response_data.get('success'):
                            print_message("system", f"Webhook procesó correctamente pero no envió mensaje por Twilio")
                            print_message("system", f"Respuesta: {response_data.get('message', 'Sin respuesta')}")
                        else:
                            error_message = response_data.get('message', 'Error desconocido')
                            print_message("error", error_message)
                else:
                    error_data = response.data if hasattr(response, 'data') else {}
                    error_message = error_data.get('error', f'HTTP {response.status_code}')
                    print_message("error", f"Error del webhook: {error_message}")
                    
            except Exception as e:
                print_message("error", f"Error al procesar el mensaje: {str(e)}")
                import traceback
                print(f"{Colors.FAIL}{traceback.format_exc()}{Colors.ENDC}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}👋 Sesión interrumpida por el usuario.{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Total de mensajes enviados: {message_count}{Colors.ENDC}\n")
            break
        except EOFError:
            print(f"\n\n{Colors.WARNING}👋 Fin de entrada detectado.{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Total de mensajes enviados: {message_count}{Colors.ENDC}\n")
            break


if __name__ == '__main__':
    main()
