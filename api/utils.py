"""
Utilidades para el manejo de requests y autenticación.
"""
from .services.auth_token_service import get_usuario_id_from_token


def get_usuario_id_from_request(request):
    """
    Obtiene el usuario_id del request desde el access_token.
    Busca el token en el header Authorization (Bearer token) o en query params.
    """
    # Intentar desde header Authorization
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        access_token = auth_header.replace('Bearer ', '').strip()
        usuario_id = get_usuario_id_from_token(access_token)
        if usuario_id:
            return usuario_id
    
    # Fallback a query param (para compatibilidad)
    access_token = request.query_params.get('access_token')
    if access_token:
        usuario_id = get_usuario_id_from_token(access_token)
        if usuario_id:
            return usuario_id
    
    return None
