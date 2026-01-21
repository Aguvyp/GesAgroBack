"""
Script CLI mejorado para simular mensajes de WhatsApp sin enviar respuestas reales por Twilio.

Este script:
- Llama directamente al controlador de WhatsApp (sin pasar por el webhook completo)
- No intenta enviar respuestas por Twilio
- Muestra las respuestas en la consola
- Permite depurar el flujo completo de procesamiento

Uso:
    python test_whatsapp_debug.py
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.controllers.whatsapp_controller import process_whatsapp_message
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


def print_banner():
    """Imprime el banner de inicio"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("  🤖 SIMULADOR DE WHATSAPP - DEBUG MODE")
    print("=" * 80)
    print(f"{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Modo de depuración: Procesa mensajes sin enviar respuestas por Twilio.")
    print(f"Escribe mensajes como si estuvieras en WhatsApp y ve las respuestas del agente.{Colors.ENDC}\n")


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
        return None, None
    
    print(f"\n{Colors.OKGREEN}Usuarios disponibles:{Colors.ENDC}")
    for i, user in enumerate(users_with_phone, 1):
        phone = normalize_phone_number(user.telefono)
        print(f"  {i}. {user.email} - {phone}")
    
    # Si solo hay un usuario, usarlo automáticamente
    if users_with_phone.count() == 1:
        user = users_with_phone.first()
        phone = normalize_phone_number(user.telefono)
        print(f"\n{Colors.OKGREEN}✅ Usando automáticamente: {user.email} ({phone}){Colors.ENDC}")
        return phone, user
    
    # Si hay múltiples usuarios, pedir selección
    while True:
        try:
            choice = input(f"\n{Colors.OKCYAN}Selecciona un usuario (1-{users_with_phone.count()}): {Colors.ENDC}")
            choice_num = int(choice)
            if 1 <= choice_num <= users_with_phone.count():
                user = list(users_with_phone)[choice_num - 1]
                phone = normalize_phone_number(user.telefono)
                print(f"{Colors.OKGREEN}✅ Seleccionado: {user.email} ({phone}){Colors.ENDC}")
                return phone, user
            else:
                print(f"{Colors.FAIL}Por favor, selecciona un número válido.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Por favor, ingresa un número.{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Cancelado por el usuario.{Colors.ENDC}")
            return None, None


def print_message(role: str, message: str):
    """Imprime un mensaje formateado"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if role == "user":
        print(f"\n{Colors.OKBLUE}[{timestamp}] 👤 Tú:{Colors.ENDC}")
        print(f"  {message}")
    elif role == "assistant":
        print(f"\n{Colors.OKGREEN}[{timestamp}] 🤖 Asistente:{Colors.ENDC}")
        # Dividir mensaje en líneas para mejor formato
        for line in message.split('\n'):
            print(f"  {line}")
    elif role == "system":
        print(f"\n{Colors.WARNING}[{timestamp}] ⚙️  Sistema:{Colors.ENDC}")
        print(f"  {message}")
    elif role == "error":
        print(f"\n{Colors.FAIL}[{timestamp}] ❌ Error:{Colors.ENDC}")
        print(f"  {message}")


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
    
    # Obtener teléfono y usuario de prueba
    test_phone, test_user = get_test_phone()
    if not test_phone or not test_user:
        return
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}=" * 80)
    print("  SESIÓN INICIADA")
    print("=" * 80 + f"{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Escribe tus mensajes y presiona Enter.{Colors.ENDC}\n")
    
    # Mostrar ayuda inicial
    print_help()
    
    # Loop principal
    message_count = 0
    while True:
        try:
            # Leer mensaje del usuario
            user_input = input(f"\n{Colors.BOLD}> {Colors.ENDC}").strip()
            
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
            
            # Mostrar mensaje del usuario
            print_message("user", user_input)
            
            # Procesar mensaje directamente con el controlador
            print_message("system", "Procesando mensaje...")
            
            try:
                # Llamar directamente al controlador (sin pasar por el webhook)
                success, response_message = process_whatsapp_message(
                    phone=test_phone,
                    message_text=user_input,
                    audio_url=None
                )
                
                message_count += 1
                
                # Mostrar respuesta
                if success:
                    print_message("assistant", response_message)
                else:
                    print_message("error", response_message)
                    
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
