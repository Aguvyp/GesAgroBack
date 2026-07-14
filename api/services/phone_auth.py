"""Servicio ligero para mapear números de teléfono a usuarios."""
from django.core.cache import cache
from ..models import Personal, Usuario


def normalize_phone_number(phone: str) -> str:
    normalized = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    if not normalized.startswith('+'):
        if normalized.startswith('54'):
            normalized = '+' + normalized
        elif normalized.startswith('9') and len(normalized) == 10:
            normalized = '+54' + normalized
        elif len(normalized) == 10 and not normalized.startswith('0'):
            normalized = '+549' + normalized

    return normalized


def get_user_by_phone(phone: str) -> Usuario | None:
    import logging
    logger = logging.getLogger(__name__)

    normalized_phone = normalize_phone_number(phone)
    logger.debug(f"Buscando usuario con teléfono normalizado: {normalized_phone}")

    cache_key = f'telegram_user_{normalized_phone}'
    user_id = cache.get(cache_key)

    if user_id:
        try:
            user = Usuario.objects.get(id=user_id)
            logger.debug(f"Usuario encontrado en cache: {user.email}")
            return user
        except Usuario.DoesNotExist:
            cache.delete(cache_key)

    try:
        user = Usuario.objects.get(telefono=normalized_phone)
        logger.debug(f"Usuario encontrado por teléfono directo: {user.email}")
        cache.set(cache_key, user.id, timeout=3600)
        return user
    except Usuario.DoesNotExist:
        logger.debug("No se encontró usuario con teléfono directo")
    except Usuario.MultipleObjectsReturned:
        user = Usuario.objects.filter(telefono=normalized_phone, is_active=True).first()
        if user:
            logger.debug(f"Usuario encontrado (múltiples resultados, tomando el primero activo): {user.email}")
            cache.set(cache_key, user.id, timeout=3600)
            return user

    try:
        personal = Personal.objects.get(telefono=normalized_phone)
        logger.debug(f"Personal encontrado: {personal.nombre}")
        try:
            user = Usuario.objects.get(nombre=personal.nombre)
            logger.debug(f"Usuario encontrado por nombre de personal: {user.email}")
            cache.set(cache_key, user.id, timeout=3600)
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

    from ..models import Cliente
    try:
        cliente = Cliente.objects.get(telefono=normalized_phone)
        logger.debug(f"Cliente encontrado: {cliente.nombre}")
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
