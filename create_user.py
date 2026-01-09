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

    # Verificar si el usuario ya existe
    if Usuario.objects.filter(email=email).exists():
        print(f'⚠ El usuario con email {email} ya existe.')
        usuario = Usuario.objects.get(email=email)
        print(f'✓ Usuario existente encontrado: {usuario.nombre}')
        return usuario

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

    print(f'''
✓ Usuario creado exitosamente!
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

