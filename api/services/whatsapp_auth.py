"""
Servicio de autenticación por número de teléfono para WhatsApp.
Mapea números de teléfono a usuarios del sistema.
"""
from django.core.cache import cache
from ..models import Personal, Usuario


def normalize_phone_number(phone: str) -> str:
    """
    Normaliza un número de teléfono eliminando espacios, guiones y caracteres especiales.
    Mantiene solo números y el prefijo + si existe.
    
    Args:
        phone: Número de teléfono en cualquier formato
        
    Returns:
        Número normalizado (ej: +5491123456789)
    """
    # Eliminar espacios, guiones, paréntesis
    normalized = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Si no empieza con +, agregarlo si parece ser internacional
    if not normalized.startswith('+'):
        # Si empieza con 54 (Argentina), agregar +
        if normalized.startswith('54'):
            normalized = '+' + normalized
        # Si empieza con 9 y tiene 10 dígitos, asumir que es +549
        elif normalized.startswith('9') and len(normalized) == 10:
            normalized = '+54' + normalized
        # Si tiene 10 dígitos y no empieza con 0, asumir +549
        elif len(normalized) == 10 and not normalized.startswith('0'):
            normalized = '+549' + normalized
    
    return normalized


def get_user_by_phone(phone: str) -> Usuario | None:
    """
    Obtiene un usuario por su número de teléfono.
    Busca primero en Usuario.telefono, luego en Personal.telefono y Cliente.telefono.
    
    Args:
        phone: Número de teléfono normalizado
        
    Returns:
        Usuario si se encuentra, None si no
    """
    import logging
    logger = logging.getLogger(__name__)
    
    normalized_phone = normalize_phone_number(phone)
    logger.debug(f"Buscando usuario con teléfono normalizado: {normalized_phone}")
    
    # Buscar en cache primero
    cache_key = f'whatsapp_user_{normalized_phone}'
    user_id = cache.get(cache_key)
    
    if user_id:
        try:
            user = Usuario.objects.get(id=user_id)
            logger.debug(f"Usuario encontrado en cache: {user.email}")
            return user
        except Usuario.DoesNotExist:
            cache.delete(cache_key)
    
    # PRIMERO: Buscar directamente en Usuario.telefono
    try:
        user = Usuario.objects.get(telefono=normalized_phone)
        logger.debug(f"Usuario encontrado por teléfono directo: {user.email}")
        # Guardar en cache para próximas búsquedas
        cache.set(cache_key, user.id, timeout=3600)  # 1 hora
        return user
    except Usuario.DoesNotExist:
        logger.debug("No se encontró usuario con teléfono directo")
    except Usuario.MultipleObjectsReturned:
        # Si hay múltiples, tomar el primero activo
        user = Usuario.objects.filter(telefono=normalized_phone, is_active=True).first()
        if user:
            logger.debug(f"Usuario encontrado (múltiples resultados, tomando el primero activo): {user.email}")
            cache.set(cache_key, user.id, timeout=3600)
            return user
    
    # SEGUNDO: Buscar en Personal por teléfono
    try:
        personal = Personal.objects.get(telefono=normalized_phone)
        logger.debug(f"Personal encontrado: {personal.nombre}")
        # Intentar encontrar usuario por nombre (ya que no hay relación directa)
        try:
            user = Usuario.objects.get(nombre=personal.nombre)
            logger.debug(f"Usuario encontrado por nombre de personal: {user.email}")
            # Guardar en cache para próximas búsquedas
            cache.set(cache_key, user.id, timeout=3600)  # 1 hora
            return user
        except Usuario.DoesNotExist:
            logger.debug("No se encontró usuario con el nombre del personal")
        except Usuario.MultipleObjectsReturned:
            user = Usuario.objects.filter(nombre=personal.nombre, is_active=True).first()
            if user:
                logger.debug(f"Usuario encontrado (múltiples por nombre): {user.email}")
                cache.set(cache_key, user.id, timeout=3600)
                return user
    except Personal.DoesNotExist:
        logger.debug("No se encontró personal con ese teléfono")
    except Personal.MultipleObjectsReturned:
        personal = Personal.objects.filter(telefono=normalized_phone).first()
        if personal:
            try:
                user = Usuario.objects.get(nombre=personal.nombre)
                logger.debug(f"Usuario encontrado (múltiples personal): {user.email}")
                cache.set(cache_key, user.id, timeout=3600)
                return user
            except Usuario.DoesNotExist:
                pass
    
    # TERCERO: Buscar en Cliente por teléfono (por si acaso)
    from ..models import Cliente
    try:
        cliente = Cliente.objects.get(telefono=normalized_phone)
        logger.debug(f"Cliente encontrado: {cliente.nombre}")
        # Intentar encontrar usuario por nombre
        try:
            user = Usuario.objects.get(nombre=cliente.nombre)
            logger.debug(f"Usuario encontrado por nombre de cliente: {user.email}")
            cache.set(cache_key, user.id, timeout=3600)
            return user
        except Usuario.DoesNotExist:
            logger.debug("No se encontró usuario con el nombre del cliente")
    except Cliente.DoesNotExist:
        logger.debug("No se encontró cliente con ese teléfono")
    except Cliente.MultipleObjectsReturned:
        cliente = Cliente.objects.filter(telefono=normalized_phone).first()
        if cliente:
            try:
                user = Usuario.objects.get(nombre=cliente.nombre)
                logger.debug(f"Usuario encontrado (múltiples clientes): {user.email}")
                cache.set(cache_key, user.id, timeout=3600)
                return user
            except Usuario.DoesNotExist:
                pass
    
    logger.warning(f"No se encontró usuario para el teléfono: {normalized_phone}")
    return None


def is_authorized_phone(phone: str) -> bool:
    """
    Verifica si un número de teléfono está autorizado.
    
    Args:
        phone: Número de teléfono
        
    Returns:
        True si está autorizado, False si no
    """
    import logging
    logger = logging.getLogger(__name__)
    
    normalized_phone = normalize_phone_number(phone)
    logger.debug(f"Verificando autorización para teléfono: {normalized_phone}")
    
    user = get_user_by_phone(phone)
    
    if user is None:
        logger.warning(f"Usuario no encontrado para teléfono: {normalized_phone}")
        return False
    
    if not user.is_active:
        logger.warning(f"Usuario encontrado pero inactivo: {user.email}")
        return False
    
    logger.info(f"Usuario autorizado: {user.email} (ID: {user.id})")
    return True
