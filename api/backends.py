from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(BaseBackend):
    """
    Backend de autenticación personalizado que usa email en lugar de username
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        # Obtener email de kwargs si no viene como parámetro
        if email is None:
            email = kwargs.get('email')
        
        if email is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Retornar None en lugar de hacer raise para que Django pruebe otros backends
            return None
        
        # Verificar la contraseña usando check_password de Django
        # Este método automáticamente:
        # 1. Hashea la contraseña en texto plano usando el mismo algoritmo que se usó al guardarla
        # 2. Compara el hash resultante con el hash almacenado en la base de datos
        # 3. Retorna True si coinciden, False en caso contrario
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        """
        Verifica si el usuario puede autenticarse (está activo)
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

