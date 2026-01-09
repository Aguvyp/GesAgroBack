from django.core.management.base import BaseCommand
from api.models import Usuario, Personal


class Command(BaseCommand):
    help = 'Crea un usuario de prueba para desarrollo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='test@gesagro.com',
            help='Email del usuario (default: test@gesagro.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='test123',
            help='Password del usuario (default: test123)'
        )
        parser.add_argument(
            '--nombre',
            type=str,
            default='Usuario de Prueba',
            help='Nombre del usuario (default: Usuario de Prueba)'
        )
        parser.add_argument(
            '--rol',
            type=str,
            choices=['Administrador', 'Contable', 'Operario'],
            default='Administrador',
            help='Rol del usuario (default: Administrador)'
        )
        parser.add_argument(
            '--dni',
            type=str,
            default='12345678',
            help='DNI del personal (default: 12345678)'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        nombre = options['nombre']
        rol = options['rol']
        dni = options['dni']

        # Verificar si el usuario ya existe
        if Usuario.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario con email {email} ya existe.')
            )
            return

        # Crear usuario
        usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            nombre=nombre,
            rol=rol
        )

        # Crear perfil de personal asociado
        Personal.objects.create(
            nombre=nombre,
            dni=dni,
            telefono='+5491123456789',
            usuario=usuario
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Usuario creado exitosamente!\n'
                f'  Email: {email}\n'
                f'  Password: {password}\n'
                f'  Nombre: {nombre}\n'
                f'  Rol: {rol}\n'
                f'  DNI: {dni}\n'
                f'\nPuedes usar estas credenciales para hacer login en /api/auth/login/'
            )
        )
