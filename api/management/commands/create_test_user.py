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

        usuario, created = Usuario.objects.get_or_create(
            email=email,
            defaults={
                'nombre': nombre,
                'rol': rol,
            },
        )
        usuario.nombre = nombre
        usuario.rol = rol
        usuario.is_active = True
        usuario.set_password(password)
        usuario.save()

        personal = Personal.objects.filter(usuario_id=usuario.id).first()
        if personal is None:
            personal = Personal.objects.filter(dni=dni).first()

        if personal is None:
            Personal.objects.create(
                nombre=nombre,
                dni=dni,
                telefono='+5491123456789',
                usuario_id=usuario.id
            )
        else:
            personal.nombre = nombre
            personal.dni = dni
            personal.telefono = personal.telefono or '+5491123456789'
            personal.usuario_id = usuario.id
            personal.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nOK Usuario {"creado" if created else "actualizado"} exitosamente!\n'
                f'  Email: {email}\n'
                f'  Password: {password}\n'
                f'  Nombre: {nombre}\n'
                f'  Rol: {rol}\n'
                f'  DNI: {dni}\n'
                f'\nPuedes usar estas credenciales para hacer login en /api/auth/login/'
            )
        )
