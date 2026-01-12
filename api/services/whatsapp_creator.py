"""
Servicio de creación de registros.
Llama a los serializers para crear trabajos, costos, campos y clientes.
"""
from typing import Dict, Tuple, Optional
from ..models import Trabajo, Costo, Campo, Cliente
from ..serializers import TrabajoSerializer, CostoSerializer, CampoSerializer, ClienteSerializer
import logging

logger = logging.getLogger(__name__)


def create_trabajo(data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Crea un trabajo usando el serializer.
    
    Args:
        data: Diccionario con datos del trabajo
        
    Returns:
        Tupla (éxito, mensaje_error, datos_creados)
    """
    try:
        # Mapear campo_id a campo (el serializer espera 'campo' con el ID)
        if 'campo_id' in data:
            data['campo'] = data['campo_id']
            del data['campo_id']
        
        # Eliminar campo_nombre si existe (es solo para logging)
        if 'campo_nombre' in data:
            del data['campo_nombre']
        
        # Mapear id_tipo_trabajo si viene como nombre
        if 'id_tipo_trabajo' not in data and 'tipo_trabajo' in data:
            from .whatsapp_validator import find_work_type_by_name
            tipo = find_work_type_by_name(data['tipo_trabajo'])
            if tipo:
                data['id_tipo_trabajo'] = tipo.id
                del data['tipo_trabajo']
        
        logger.debug(f"   Datos finales para serializer: {data}")
        # Verificar que usuario_id está presente
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")
        
        serializer = TrabajoSerializer(data=data)
        
        if serializer.is_valid():
            logger.debug("   ✓ Serializer válido, creando trabajo...")
            trabajo = serializer.save()
            logger.info(f"   ✅ Trabajo creado exitosamente: ID {trabajo.id}")
            logger.debug(f"   Detalles del trabajo creado:")
            logger.debug(f"      - ID: {trabajo.id}")
            logger.debug(f"      - usuario_id: {trabajo.usuario_id}")
            logger.debug(f"      - Tipo: {trabajo.id_tipo_trabajo.trabajo if trabajo.id_tipo_trabajo else None}")
            logger.debug(f"      - Cultivo: {trabajo.cultivo}")
            logger.debug(f"      - Campo: {trabajo.campo.nombre if trabajo.campo else None}")
            logger.debug(f"      - Fecha inicio: {trabajo.fecha_inicio}")
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
    """
    Crea un costo usando el serializer.
    
    Args:
        data: Diccionario con datos del costo
        
    Returns:
        Tupla (éxito, mensaje_error, datos_creados)
    """
    try:
        # Verificar que usuario_id está presente
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")
        
        serializer = CostoSerializer(data=data)
        if serializer.is_valid():
            costo = serializer.save()
            logger.info(f"Costo creado exitosamente: ID {costo.id}, usuario_id: {costo.usuario_id}")
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
    """
    Crea un campo usando el serializer.
    
    Args:
        data: Diccionario con datos del campo
        
    Returns:
        Tupla (éxito, mensaje_error, datos_creados)
    """
    try:
        # Verificar que usuario_id está presente
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")
        
        serializer = CampoSerializer(data=data)
        if serializer.is_valid():
            campo = serializer.save()
            logger.info(f"Campo creado exitosamente: ID {campo.id}, usuario_id: {campo.usuario_id}")
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
    """
    Crea un cliente usando el serializer.
    
    Args:
        data: Diccionario con datos del cliente
        
    Returns:
        Tupla (éxito, mensaje_error, datos_creados)
    """
    try:
        # Verificar que usuario_id está presente
        if 'usuario_id' in data:
            logger.info(f"   ✅ usuario_id presente: {data['usuario_id']}")
        else:
            logger.warning("   ⚠️ usuario_id NO está presente en los datos")
        
        serializer = ClienteSerializer(data=data)
        if serializer.is_valid():
            cliente = serializer.save()
            logger.info(f"Cliente creado exitosamente: ID {cliente.id}, usuario_id: {cliente.usuario_id}")
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
