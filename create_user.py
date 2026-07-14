"""
Script simple para crear un usuario de prueba
Ejecutar con: python create_user.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Usuario, Personal

def create_test_user():
    email = 'test@gesagro.com'
    password = 'test123'
    nombre = 'Usuario de Prueba'
    rol = 'Administrador'
    dni = '12345678'

    usuario, _created = Usuario.objects.get_or_create(
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

    print(f'''
OK Usuario listo exitosamente!
  Email: {email}
  Password: {password}
  Nombre: {nombre}
  Rol: {rol}
  DNI: {dni}

Puedes usar estas credenciales para hacer login en /api/auth/login/
''')
    return usuario

if __name__ == '__main__':
    create_test_user()

