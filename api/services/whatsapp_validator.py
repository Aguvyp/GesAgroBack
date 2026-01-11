"""
Validador de referencias en la base de datos.
Verifica que campos, clientes, tipos de trabajo, etc. existan antes de crear registros.
"""
from typing import Dict, Optional, Tuple
from ..models import Campo, Cliente, TipoTrabajo, Personal, Maquina
import logging

logger = logging.getLogger(__name__)


def find_field_by_name(name: str) -> Optional[Campo]:
    """
    Busca un campo por nombre (búsqueda parcial, case-insensitive).
    
    Args:
        name: Nombre del campo a buscar
        
    Returns:
        Campo si se encuentra, None si no
    """
    try:
        # Buscar coincidencia exacta primero
        campo = Campo.objects.get(nombre__iexact=name)
        return campo
    except Campo.DoesNotExist:
        # Buscar coincidencia parcial
        try:
            campo = Campo.objects.filter(nombre__icontains=name).first()
            return campo
        except Exception:
            return None
    except Campo.MultipleObjectsReturned:
        # Si hay múltiples, tomar el primero
        return Campo.objects.filter(nombre__iexact=name).first()
    except Exception as e:
        logger.error(f"Error buscando campo: {str(e)}")
        return None


def find_client_by_name(name: str) -> Optional[Cliente]:
    """
    Busca un cliente por nombre (búsqueda parcial, case-insensitive).
    
    Args:
        name: Nombre del cliente a buscar
        
    Returns:
        Cliente si se encuentra, None si no
    """
    try:
        cliente = Cliente.objects.get(nombre__iexact=name)
        return cliente
    except Cliente.DoesNotExist:
        try:
            cliente = Cliente.objects.filter(nombre__icontains=name).first()
            return cliente
        except Exception:
            return None
    except Cliente.MultipleObjectsReturned:
        return Cliente.objects.filter(nombre__iexact=name).first()
    except Exception as e:
        logger.error(f"Error buscando cliente: {str(e)}")
        return None


def find_work_type_by_name(name: str) -> Optional[TipoTrabajo]:
    """
    Busca un tipo de trabajo por nombre (búsqueda parcial, case-insensitive).
    
    Args:
        name: Nombre del tipo de trabajo
        
    Returns:
        TipoTrabajo si se encuentra, None si no
    """
    try:
        tipo = TipoTrabajo.objects.get(trabajo__iexact=name)
        return tipo
    except TipoTrabajo.DoesNotExist:
        try:
            tipo = TipoTrabajo.objects.filter(trabajo__icontains=name).first()
            return tipo
        except Exception:
            return None
    except TipoTrabajo.MultipleObjectsReturned:
        return TipoTrabajo.objects.filter(trabajo__iexact=name).first()
    except Exception as e:
        logger.error(f"Error buscando tipo de trabajo: {str(e)}")
        return None


def validate_trabajo_data(data: Dict) -> Tuple[bool, Optional[str], Dict]:
    """
    Valida los datos para crear un trabajo.
    
    Args:
        data: Diccionario con datos del trabajo
        
    Returns:
        Tupla (es_válido, mensaje_error, datos_validados)
    """
    logger.debug(f"   Validando datos de trabajo: {data}")
    validated_data = {}
    errors = []
    
    # Validar tipo de trabajo (puede venir como 'tipo_trabajo' o 'id_tipo_trabajo')
    logger.debug("   Validando tipo de trabajo...")
    if 'id_tipo_trabajo' in data:
        # Si ya viene el ID, validar que exista
        from ..models import TipoTrabajo
        try:
            tipo = TipoTrabajo.objects.get(id=data['id_tipo_trabajo'])
            validated_data['id_tipo_trabajo'] = tipo.id
            logger.debug(f"   ✓ Tipo de trabajo encontrado por ID: {tipo.trabajo} (ID: {tipo.id})")
        except TipoTrabajo.DoesNotExist:
            errors.append(f"No se encontró el tipo de trabajo con ID: {data['id_tipo_trabajo']}")
            logger.error(f"   ❌ Tipo de trabajo con ID {data['id_tipo_trabajo']} no existe")
    elif 'tipo_trabajo' in data:
        logger.debug(f"   Buscando tipo de trabajo por nombre: '{data['tipo_trabajo']}'")
        tipo = find_work_type_by_name(data['tipo_trabajo'])
        if not tipo:
            errors.append(f"No se encontró el tipo de trabajo: {data['tipo_trabajo']}")
            logger.error(f"   ❌ Tipo de trabajo '{data['tipo_trabajo']}' no encontrado en BD")
        else:
            validated_data['id_tipo_trabajo'] = tipo.id
            logger.debug(f"   ✓ Tipo de trabajo encontrado: {tipo.trabajo} (ID: {tipo.id})")
    else:
        errors.append("El tipo de trabajo es requerido")
        logger.error("   ❌ Tipo de trabajo no proporcionado")
    
    # Validar campo (puede venir como 'campo' o 'campo_id')
    logger.debug("   Validando campo...")
    if 'campo_id' in data:
        # Si ya viene el ID, validar que exista
        from ..models import Campo
        try:
            campo = Campo.objects.get(id=data['campo_id'])
            validated_data['campo_id'] = campo.id
            logger.debug(f"   ✓ Campo encontrado por ID: {campo.nombre} (ID: {campo.id})")
        except Campo.DoesNotExist:
            errors.append(f"No se encontró el campo con ID: {data['campo_id']}")
            logger.error(f"   ❌ Campo con ID {data['campo_id']} no existe")
    elif 'campo' in data:
        logger.debug(f"   Buscando campo por nombre: '{data['campo']}'")
        campo = find_field_by_name(data['campo'])
        if not campo:
            errors.append(f"No se encontró el campo: {data['campo']}")
            logger.error(f"   ❌ Campo '{data['campo']}' no encontrado en BD")
        else:
            validated_data['campo_id'] = campo.id
            validated_data['campo_nombre'] = campo.nombre
            logger.debug(f"   ✓ Campo encontrado: {campo.nombre} (ID: {campo.id})")
    else:
        errors.append("El campo es requerido")
        logger.error("   ❌ Campo no proporcionado")
    
    # Validar cultivo (opcional)
    logger.debug("   Validando cultivo...")
    if 'cultivo' in data and data['cultivo']:
        validated_data['cultivo'] = data['cultivo']
        logger.debug(f"   ✓ Cultivo: {data['cultivo']}")
    else:
        # Si no viene cultivo, usar valor por defecto
        validated_data['cultivo'] = 'Sin especificar'
        logger.debug("   ✓ Cultivo: Sin especificar (valor por defecto)")
    
    # Validar fecha_inicio (requerida)
    logger.debug("   Validando fecha de inicio...")
    if 'fecha_inicio' in data and data['fecha_inicio']:
        validated_data['fecha_inicio'] = data['fecha_inicio']
        logger.debug(f"   ✓ Fecha inicio: {data['fecha_inicio']}")
    else:
        errors.append("La fecha de inicio es requerida")
        logger.error("   ❌ Fecha de inicio no proporcionada")
    
    # Fecha fin (opcional)
    if 'fecha_fin' in data and data['fecha_fin']:
        validated_data['fecha_fin'] = data['fecha_fin']
    
    # Cliente (opcional)
    if 'cliente' in data and data['cliente']:
        validated_data['cliente'] = data['cliente']
    
    # Observaciones (opcional)
    if 'observaciones' in data:
        validated_data['observaciones'] = data['observaciones']
    
    # Estado (opcional, por defecto 'Pendiente')
    if 'estado' in data and data['estado']:
        validated_data['estado'] = data['estado']
    else:
        validated_data['estado'] = 'Pendiente'
    
    if errors:
        return False, "; ".join(errors), {}
    
    return True, None, validated_data


def validate_costo_data(data: Dict) -> Tuple[bool, Optional[str], Dict]:
    """
    Valida los datos para crear un costo.
    
    Args:
        data: Diccionario con datos del costo
        
    Returns:
        Tupla (es_válido, mensaje_error, datos_validados)
    """
    validated_data = {}
    errors = []
    
    # Validar monto (requerido)
    if 'monto' in data and data['monto']:
        validated_data['monto'] = float(data['monto'])
    else:
        errors.append("El monto es requerido")
    
    # Validar fecha (requerida)
    if 'fecha' in data and data['fecha']:
        validated_data['fecha'] = data['fecha']
    else:
        errors.append("La fecha es requerida")
    
    # Destinatario (requerido, pero si no viene, usar descripción o valor por defecto)
    if 'destinatario' in data and data['destinatario']:
        validated_data['destinatario'] = data['destinatario']
        logger.debug(f"   ✓ Destinatario: {data['destinatario']}")
    elif 'descripcion' in data and data['descripcion']:
        # Si no hay destinatario pero hay descripción, usar la descripción
        validated_data['destinatario'] = data['descripcion']
        logger.debug(f"   ✓ Destinatario (de descripción): {data['descripcion']}")
    else:
        # Si no hay ninguno, usar valor por defecto
        validated_data['destinatario'] = 'Sin especificar'
        logger.warning("   ⚠️ No se encontró destinatario, usando 'Sin especificar'")
    
    # Descripción (opcional)
    if 'descripcion' in data:
        validated_data['descripcion'] = data['descripcion']
    
    # Categoría (opcional)
    if 'categoria' in data:
        validated_data['categoria'] = data['categoria']
    
    if errors:
        return False, "; ".join(errors), {}
    
    return True, None, validated_data


def validate_campo_data(data: Dict) -> Tuple[bool, Optional[str], Dict]:
    """
    Valida los datos para crear un campo.
    
    Args:
        data: Diccionario con datos del campo
        
    Returns:
        Tupla (es_válido, mensaje_error, datos_validados)
    """
    validated_data = {}
    errors = []
    
    # Validar nombre (requerido)
    if 'nombre' in data and data['nombre']:
        validated_data['nombre'] = data['nombre']
    else:
        errors.append("El nombre del campo es requerido")
    
    # Hectáreas (opcional)
    if 'hectareas' in data and data['hectareas']:
        validated_data['hectareas'] = float(data['hectareas'])
    
    # Detalles (opcional)
    if 'detalles' in data:
        validated_data['detalles'] = data['detalles']
    
    if errors:
        return False, "; ".join(errors), {}
    
    return True, None, validated_data


def validate_cliente_data(data: Dict) -> Tuple[bool, Optional[str], Dict]:
    """
    Valida los datos para crear un cliente.
    
    Args:
        data: Diccionario con datos del cliente
        
    Returns:
        Tupla (es_válido, mensaje_error, datos_validados)
    """
    validated_data = {}
    errors = []
    
    # Validar nombre (requerido)
    if 'nombre' in data and data['nombre']:
        validated_data['nombre'] = data['nombre']
    else:
        errors.append("El nombre del cliente es requerido")
    
    # Email (opcional)
    if 'email' in data:
        validated_data['email'] = data['email']
    
    # Teléfono (opcional)
    if 'telefono' in data:
        validated_data['telefono'] = data['telefono']
    
    # Dirección (opcional)
    if 'direccion' in data:
        validated_data['direccion'] = data['direccion']
    
    if errors:
        return False, "; ".join(errors), {}
    
    return True, None, validated_data
