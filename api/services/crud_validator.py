"""Validador de referencias en la base de datos para el agente."""
from typing import Dict, Optional, Tuple
from ..models import Campo, Cliente, TipoTrabajo, Personal
import logging

logger = logging.getLogger(__name__)


def find_field_by_name(name: str, usuario_id: Optional[int] = None) -> Optional[Campo]:
    try:
        queryset = Campo.objects.all()
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)

        campo = queryset.get(nombre__iexact=name)
        return campo
    except Campo.DoesNotExist:
        try:
            campo = queryset.filter(nombre__icontains=name).first()
            return campo
        except Exception:
            return None
    except Campo.MultipleObjectsReturned:
        return queryset.filter(nombre__iexact=name).first()
    except Exception as e:
        logger.error(f"Error buscando campo: {str(e)}")
        return None


def find_client_by_name(name: str, usuario_id: Optional[int] = None) -> Optional[Cliente]:
    try:
        queryset = Cliente.objects.all()
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)

        cliente = queryset.get(nombre__iexact=name)
        return cliente
    except Cliente.DoesNotExist:
        try:
            cliente = queryset.filter(nombre__icontains=name).first()
            return cliente
        except Exception:
            return None
    except Cliente.MultipleObjectsReturned:
        return queryset.filter(nombre__iexact=name).first()
    except Exception as e:
        logger.error(f"Error buscando cliente: {str(e)}")
        return None


def find_work_type_by_name(name: str) -> Optional[TipoTrabajo]:
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
    logger.debug(f"   Validando datos de trabajo: {data}")
    validated_data = {}
    errors = []

    if 'usuario_id' in data:
        validated_data['usuario_id'] = data['usuario_id']
        logger.debug(f"   ✓ usuario_id preservado: {data['usuario_id']}")

    logger.debug("   Validando tipo de trabajo...")
    if 'id_tipo_trabajo' in data:
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

    logger.debug("   Validando campo...")
    if 'campo_id' in data:
        from ..models import Campo
        try:
            queryset = Campo.objects.filter(id=data['campo_id'])
            if 'usuario_id' in data and data['usuario_id']:
                queryset = queryset.filter(usuario_id=data['usuario_id'])
            campo = queryset.first()
            if campo:
                validated_data['campo_id'] = campo.id
                logger.debug(f"   ✓ Campo encontrado por ID: {campo.nombre} (ID: {campo.id})")
            else:
                errors.append(f"No se encontró el campo con ID: {data['campo_id']} o no pertenece al usuario")
                logger.error(f"   ❌ Campo con ID {data['campo_id']} no existe o no pertenece al usuario")
        except Exception as e:
            errors.append(f"Error validando campo: {str(e)}")
            logger.error(f"   ❌ Error validando campo: {str(e)}")
    elif 'campo' in data:
        logger.debug(f"   Buscando campo por nombre: '{data['campo']}'")
        usuario_id = data.get('usuario_id')
        campo = find_field_by_name(data['campo'], usuario_id=usuario_id)
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

    logger.debug("   Validando cultivo...")
    if 'cultivo' in data and data['cultivo']:
        validated_data['cultivo'] = data['cultivo']
        logger.debug(f"   ✓ Cultivo: {data['cultivo']}")
    else:
        validated_data['cultivo'] = 'Sin especificar'
        logger.debug("   ✓ Cultivo: Sin especificar (valor por defecto)")

    logger.debug("   Validando fecha de inicio...")
    if 'fecha_inicio' in data and data['fecha_inicio']:
        validated_data['fecha_inicio'] = data['fecha_inicio']
        logger.debug(f"   ✓ Fecha inicio: {data['fecha_inicio']}")
    else:
        errors.append("La fecha de inicio es requerida")
        logger.error("   ❌ Fecha de inicio no proporcionada")

    if 'fecha_fin' in data and data['fecha_fin']:
        validated_data['fecha_fin'] = data['fecha_fin']

    if 'cliente' in data and data['cliente']:
        validated_data['cliente'] = data['cliente']

    if 'observaciones' in data:
        validated_data['observaciones'] = data['observaciones']

    if 'estado' in data and data['estado']:
        validated_data['estado'] = data['estado']
    else:
        validated_data['estado'] = 'Pendiente'

    if errors:
        return False, "; ".join(errors), {}

    return True, None, validated_data


def validate_costo_data(data: Dict) -> Tuple[bool, Optional[str], Dict]:
    validated_data = {}
    errors = []

    if 'usuario_id' in data:
        validated_data['usuario_id'] = data['usuario_id']
        logger.debug(f"   ✓ usuario_id preservado: {data['usuario_id']}")

    if 'monto' in data and data['monto']:
        validated_data['monto'] = float(data['monto'])
    else:
        errors.append("El monto es requerido")

    if 'fecha' in data and data['fecha']:
        validated_data['fecha'] = data['fecha']
    else:
        errors.append("La fecha es requerida")

    if 'destinatario' in data and data['destinatario']:
        validated_data['destinatario'] = data['destinatario']
        logger.debug(f"   ✓ Destinatario: {data['destinatario']}")
    elif 'descripcion' in data and data['descripcion']:
        validated_data['destinatario'] = data['descripcion']
        logger.debug(f"   ✓ Destinatario (de descripción): {data['descripcion']}")
    else:
        validated_data['destinatario'] = 'Sin especificar'
        logger.warning("   ⚠️ No se encontró destinatario, usando 'Sin especificar'")

    if 'descripcion' in data:
        validated_data['descripcion'] = data['descripcion']

    if 'categoria' in data:
        validated_data['categoria'] = data['categoria']

    if errors:
        return False, "; ".join(errors), {}

    return True, None, validated_data


def validate_campo_data(data: Dict) -> Tuple[bool, Optional[str], Dict]:
    validated_data = {}
    errors = []
    usuario_id = None
    if 'usuario_id' in data:
        usuario_id = data['usuario_id']
        validated_data['usuario_id'] = usuario_id
        logger.debug(f"   ✓ usuario_id preservado: {usuario_id}")

    if 'nombre' in data and data['nombre']:
        validated_data['nombre'] = data['nombre']
    else:
        errors.append("El nombre del campo es requerido")

    if 'propio' in data:
        validated_data['propio'] = bool(data['propio'])
    else:
        validated_data['propio'] = True

    if not validated_data.get('propio', True):
        if 'cliente_id' in data and data['cliente_id']:
            cliente_id = data['cliente_id']
            if usuario_id:
                from ..models import Cliente
                try:
                    cliente = Cliente.objects.get(id=cliente_id, usuario_id=usuario_id)
                    validated_data['cliente_id'] = cliente_id
                    logger.debug(f"   ✓ Cliente validado: {cliente.nombre} (ID: {cliente_id})")
                except Cliente.DoesNotExist:
                    errors.append(f"El cliente con ID {cliente_id} no existe o no pertenece al usuario")
            else:
                from ..models import Cliente
                try:
                    cliente = Cliente.objects.get(id=cliente_id)
                    validated_data['cliente_id'] = cliente_id
                    logger.debug(f"   ✓ Cliente validado: {cliente.nombre} (ID: {cliente_id})")
                except Cliente.DoesNotExist:
                    errors.append(f"El cliente con ID {cliente_id} no existe")
        else:
            errors.append("Si el campo no es propio, debe especificar un cliente_id")
    else:
        validated_data['cliente_id'] = None

    if 'hectareas' in data and data['hectareas']:
        validated_data['hectareas'] = float(data['hectareas'])

    if 'detalles' in data:
        validated_data['detalles'] = data['detalles']

    if errors:
        return False, "; ".join(errors), {}

    return True, None, validated_data


def validate_cliente_data(data: Dict) -> Tuple[bool, Optional[str], Dict]:
    validated_data = {}
    errors = []

    if 'usuario_id' in data:
        validated_data['usuario_id'] = data['usuario_id']
        logger.debug(f"   ✓ usuario_id preservado: {data['usuario_id']}")

    if 'nombre' in data and data['nombre']:
        validated_data['nombre'] = data['nombre']
    else:
        errors.append("El nombre del cliente es requerido")

    if 'email' in data:
        validated_data['email'] = data['email']

    if 'telefono' in data:
        validated_data['telefono'] = data['telefono']

    if 'direccion' in data:
        validated_data['direccion'] = data['direccion']

    if errors:
        return False, "; ".join(errors), {}

    return True, None, validated_data
