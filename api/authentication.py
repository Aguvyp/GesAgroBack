from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone

from .models import AuthToken, Usuario


class GesAgroTokenAuthentication(BaseAuthentication):
    """Autenticación Bearer basada en los tokens emitidos por GesAgro."""

    keyword = 'Bearer'

    def authenticate(self, request):
        authorization = request.headers.get('Authorization', '').strip()
        if not authorization:
            return None

        parts = authorization.split(' ', 1)
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            raise AuthenticationFailed('Encabezado Authorization inválido')

        access_token = parts[1].strip()
        if not access_token:
            raise AuthenticationFailed('Token de acceso requerido')

        try:
            token = AuthToken.objects.get(
                access_token=access_token,
                is_active=True,
            )
        except AuthToken.DoesNotExist as exc:
            raise AuthenticationFailed('Token inválido') from exc

        if token.expires_at and token.expires_at <= timezone.now():
            token.is_active = False
            token.save(update_fields=['is_active'])
            raise AuthenticationFailed('Token expirado')

        try:
            user = Usuario.objects.get(pk=token.usuario_id, is_active=True)
        except Usuario.DoesNotExist as exc:
            raise AuthenticationFailed('Usuario inválido o inactivo') from exc

        return user, token

    def authenticate_header(self, request):
        return self.keyword
