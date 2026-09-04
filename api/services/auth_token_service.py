"""
Servicio de autenticación con tokens personalizados.
Maneja la generación, validación e invalidación de tokens de acceso.
"""
import secrets
from datetime import timedelta
from django.utils import timezone
from ..models import AuthToken, Usuario


def generate_access_token() -> str:
    """Genera un token de acceso único"""
    return secrets.token_urlsafe(32)


def create_auth_token(usuario_id: int, expires_in_days: int = 30) -> AuthToken:
    """
    Crea un token independiente para cada inicio de sesión/dispositivo.

    No se reemplaza el token anterior: hacerlo desconectaba silenciosamente el
    celular cuando el mismo usuario iniciaba sesión en otro dispositivo.
    """
    token = generate_access_token()
    expires_at = timezone.now() + timedelta(days=expires_in_days)
    
    auth_token = AuthToken.objects.create(
        usuario_id=usuario_id,
        access_token=token,
        expires_at=expires_at,
        is_active=True,
    )
    return auth_token


def get_usuario_id_from_token(access_token: str) -> int | None:
    """Obtiene el usuario_id desde un access_token"""
    try:
        auth_token = AuthToken.objects.get(
            access_token=access_token,
            is_active=True
        )
        # Verificar expiración
        if auth_token.expires_at and auth_token.expires_at < timezone.now():
            return None
        return auth_token.usuario_id
    except AuthToken.DoesNotExist:
        return None


def invalidate_token(access_token: str) -> bool:
    """Invalida un token (logout)"""
    try:
        auth_token = AuthToken.objects.get(access_token=access_token)
        auth_token.is_active = False
        auth_token.save()
        return True
    except AuthToken.DoesNotExist:
        return False
