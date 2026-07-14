"""Crea registros para cada entidad usando los serializers adecuados."""
from typing import Dict, Optional, Tuple
from ..serializers import TrabajoSerializer, CostoSerializer, CampoSerializer, ClienteSerializer
import logging

logger = logging.getLogger(__name__)


def create_trabajo(data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
    try:
        if 'campo_id' in data:
            data['campo'] = data['campo_id']
            del data['campo_id']

        if 'campo_nombre' in data:
            del data['campo_nombre']

        if 'id_tipo_trabajo' not in data and 'tipo_trabajo' in data:
            from .crud_validator import find_work_type_by_name
            tipo = find_work_type_by_name(data['tipo_trabajo'])
            if tipo:
                data['id_tipo_trabajo'] = tipo.id
                del data['tipo_trabajo']

        logger.debug(f"   Datos finales para serializer: {data}")
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")

        serializer = TrabajoSerializer(data=data)

        if serializer.is_valid():
            trabajo = serializer.save()
            logger.info(f"   ✅ Trabajo creado exitosamente: ID {trabajo.id}")
            return True, None, {
                'id': trabajo.id,
                'tipo': trabajo.id_tipo_trabajo.trabajo if trabajo.id_tipo_trabajo else None,
                'cultivo': trabajo.cultivo,
                'campo': trabajo.campo.nombre if trabajo.campo else None,
            }
        else:
            errors = "; ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
            logger.error(f"   ❌ Error en serializer: {errors}")
            logger.error(f"   Datos que causaron el error: {data}")
            return False, f"Error de validación: {errors}", None
    except Exception as e:
        logger.error(f"Error creando trabajo: {str(e)}")
        return False, f"Error al crear trabajo: {str(e)}", None


def create_costo(data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
    try:
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")

        serializer = CostoSerializer(data=data)
        if serializer.is_valid():
            costo = serializer.save()
            logger.info(f"Costo creado exitosamente: ID {costo.id}")
            return True, None, {
                'id': costo.id,
                'monto': float(costo.monto),
                'fecha': costo.fecha.isoformat() if costo.fecha else None,
                'destinatario': costo.destinatario,
            }
        else:
            errors = "; ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
            logger.error(f"Error validando costo: {errors}")
            return False, f"Error de validación: {errors}", None
    except Exception as e:
        logger.error(f"Error creando costo: {str(e)}")
        return False, f"Error al crear costo: {str(e)}", None


def create_campo(data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
    try:
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")

        serializer = CampoSerializer(data=data)
        if serializer.is_valid():
            campo = serializer.save()
            logger.info(f"Campo creado exitosamente: ID {campo.id}")
            return True, None, {
                'id': campo.id,
                'nombre': campo.nombre,
                'hectareas': float(campo.hectareas) if campo.hectareas else 0.0,
            }
        else:
            errors = "; ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
            logger.error(f"Error validando campo: {errors}")
            return False, f"Error de validación: {errors}", None
    except Exception as e:
        logger.error(f"Error creando campo: {str(e)}")
        return False, f"Error al crear campo: {str(e)}", None


def create_cliente(data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
    try:
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")

        serializer = ClienteSerializer(data=data)
        if serializer.is_valid():
            cliente = serializer.save()
            logger.info(f"Cliente creado exitosamente: ID {cliente.id}")
            return True, None, {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'email': cliente.email,
                'telefono': cliente.telefono,
            }
        else:
            errors = "; ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
            logger.error(f"Error validando cliente: {errors}")
            return False, f"Error de validación: {errors}", None
    except Exception as e:
        logger.error(f"Error creando cliente: {str(e)}")
        return False, f"Error al crear cliente: {str(e)}", None
