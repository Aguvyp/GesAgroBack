"""
Agente OpenAI con function calling para procesar mensajes de WhatsApp.
Soporta operaciones CRUD completas (Crear, Leer, Actualizar, Eliminar).
"""
import openai
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
from datetime import date
from decimal import Decimal
from django.conf import settings
from ..services.whatsapp_creator import (
    create_trabajo, create_costo, create_campo, create_cliente
)
from ..services.whatsapp_validator import (
    find_field_by_name, find_work_type_by_name, find_client_by_name,
    validate_trabajo_data, validate_costo_data, validate_campo_data, validate_cliente_data
)
from ..models import (
    Trabajo, Costo, Campo, Cliente, TipoTrabajo
)
import dateparser

logger = logging.getLogger(__name__)

# Configuración
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', '')
OPENAI_MODEL = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')


def json_serializer(obj):
    """Serializador personalizado para tipos que no son JSON serializables por defecto."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def get_openai_functions() -> List[Dict]:
    """
    Define todas las funciones disponibles para el agente OpenAI.
    
    Returns:
        Lista de definiciones de funciones en formato OpenAI
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_trabajo",
                "description": "Crea un nuevo trabajo agrícola. Requiere: tipo_trabajo (nombre), campo (nombre), fecha_inicio. Opcional: cultivo, fecha_fin, cliente, observaciones, estado. CRÍTICO: SIEMPRE crea el trabajo sin importar la fecha (pasada, presente o futura). Las fechas futuras están PERMITIDAS y son NORMALES. NO rechaces crear trabajos por la fecha. Tu función es CREAR, no validar fechas. IMPORTANTE: Si el mensaje menciona 'completado', 'terminado', 'finalizado', establece estado='Completado'. Si no se menciona, el estado por defecto es 'Pendiente'. NO uses esta función si el usuario dice 'completar', 'marcar como completado', 'terminar', 'finalizar' - en esos casos usa update_trabajo para actualizar el trabajo existente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tipo_trabajo": {
                            "type": "string",
                            "description": "Tipo de trabajo (ej: siembra, cosecha, pulverización, labranza, laboreo)"
                        },
                        "cultivo": {
                            "type": "string",
                            "description": "Nombre del cultivo (opcional) - tipo de siembra como: soja, maíz, trigo, girasol, sorgo, cebada. Solo incluir si se menciona en el mensaje."
                        },
                        "campo": {
                            "type": "string",
                            "description": "Nombre del campo donde se realizará el trabajo"
                        },
                        "fecha_inicio": {
                            "type": "string",
                            "description": "Fecha de inicio en formato YYYY-MM-DD o texto como 'hoy', 'mañana', '15/03/2024'. PERMITIDAS fechas pasadas, presentes y futuras. NO validar la fecha contra la fecha actual."
                        },
                        "fecha_fin": {
                            "type": "string",
                            "description": "Fecha de fin en formato YYYY-MM-DD (opcional)"
                        },
                        "cliente": {
                            "type": "string",
                            "description": "Nombre del cliente (opcional)"
                        },
                        "observaciones": {
                            "type": "string",
                            "description": "Observaciones adicionales (opcional)"
                        },
                        "estado": {
                            "type": "string",
                            "description": "Estado del trabajo. Si el mensaje menciona 'completado', 'terminado', 'finalizado', usar 'Completado'. Si no se menciona, usar 'Pendiente' (valor por defecto).",
                            "enum": ["Pendiente", "En Proceso", "Completado", "Cancelado"]
                        }
                    },
                    "required": ["tipo_trabajo", "campo", "fecha_inicio"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_trabajo",
                "description": "Actualiza un trabajo existente. ÚSALA cuando el usuario diga 'completar', 'marcar como completado', 'terminar', 'finalizar', 'actualizar estado', etc. Puedes buscar el trabajo por: campo + tipo_trabajo + fecha_inicio (y opcionalmente cultivo), O por ID. Si no proporcionas fecha_inicio o cultivo y hay múltiples trabajos que coinciden, primero usa get_trabajos para listarlos y preguntar al usuario cuál actualizar. Si proporcionas campo, tipo_trabajo y fecha_inicio (y opcionalmente cultivo), actualiza directamente el trabajo que coincida. Si el usuario dice 'completar', establece estado='Completado'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID del trabajo a actualizar (opcional si proporcionas campo + tipo_trabajo + fecha_inicio)"
                        },
                        "campo": {
                            "type": "string",
                            "description": "Nombre del campo para buscar el trabajo (opcional si proporcionas ID)"
                        },
                        "tipo_trabajo": {
                            "type": "string",
                            "description": "Tipo de trabajo para buscar (opcional si proporcionas ID)"
                        },
                        "fecha_inicio": {
                            "type": "string",
                            "description": "Fecha de inicio para buscar el trabajo en formato YYYY-MM-DD (opcional si proporcionas ID). Si no proporcionas fecha y hay múltiples trabajos, primero lista con get_trabajos."
                        },
                        "cultivo": {
                            "type": "string",
                            "description": "Cultivo para buscar el trabajo (opcional). Si no proporcionas cultivo y hay múltiples trabajos, primero lista con get_trabajos."
                        },
                        "estado": {
                            "type": "string",
                            "description": "Nuevo estado del trabajo",
                            "enum": ["Pendiente", "En Proceso", "Completado", "Cancelado"]
                        },
                        "fecha_fin": {"type": "string"},
                        "cliente": {"type": "string"},
                        "observaciones": {"type": "string"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_trabajo",
                "description": "Elimina un trabajo por su ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID del trabajo a eliminar"
                        }
                    },
                    "required": ["id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_trabajos",
                "description": "Obtiene lista de trabajos con filtros opcionales. Útil para listar trabajos cuando hay múltiples coincidencias antes de actualizar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campo": {"type": "string", "description": "Filtrar por nombre de campo"},
                        "tipo_trabajo": {"type": "string", "description": "Filtrar por tipo de trabajo"},
                        "cultivo": {"type": "string", "description": "Filtrar por cultivo"},
                        "estado": {"type": "string", "description": "Filtrar por estado"},
                        "limit": {"type": "integer", "description": "Límite de resultados (default: 10)"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_costo",
                "description": "Crea un nuevo costo o gasto. Requiere: monto, fecha, destinatario. Opcional: descripcion, categoria, forma_pago.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "monto": {
                            "type": "number",
                            "description": "Monto del costo"
                        },
                        "fecha": {
                            "type": "string",
                            "description": "Fecha en formato YYYY-MM-DD o 'hoy', 'mañana'"
                        },
                        "destinatario": {
                            "type": "string",
                            "description": "A quién se pagó o para qué es el gasto"
                        },
                        "descripcion": {
                            "type": "string",
                            "description": "Descripción detallada (opcional)"
                        },
                        "categoria": {
                            "type": "string",
                            "description": "Categoría del costo (opcional)"
                        },
                        "forma_pago": {
                            "type": "string",
                            "description": "Forma de pago (opcional)"
                        }
                    },
                    "required": ["monto", "fecha", "destinatario"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_costo",
                "description": "Actualiza un costo existente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID del costo"},
                        "monto": {"type": "number"},
                        "fecha": {"type": "string"},
                        "destinatario": {"type": "string"},
                        "descripcion": {"type": "string"},
                        "pagado": {"type": "boolean"}
                    },
                    "required": ["id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_costo",
                "description": "Elimina un costo por su ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"}
                    },
                    "required": ["id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_costos",
                "description": "Obtiene lista de costos con filtros opcionales.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pagado": {"type": "boolean"},
                        "limit": {"type": "integer"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_campo",
                "description": "Crea un nuevo campo. Requiere: nombre. Opcional: hectareas, detalles.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string", "description": "Nombre del campo"},
                        "hectareas": {"type": "number", "description": "Hectáreas del campo (opcional)"},
                        "detalles": {"type": "string", "description": "Detalles adicionales (opcional)"}
                    },
                    "required": ["nombre"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_campo",
                "description": "Actualiza un campo existente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nombre": {"type": "string"},
                        "hectareas": {"type": "number"},
                        "detalles": {"type": "string"}
                    },
                    "required": ["id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_campo",
                "description": "Elimina un campo por su ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"}
                    },
                    "required": ["id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_campos",
                "description": "Obtiene lista de campos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_cliente",
                "description": "Crea un nuevo cliente. Requiere: nombre. Opcional: email, telefono, direccion, cuit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string"},
                        "email": {"type": "string"},
                        "telefono": {"type": "string"},
                        "direccion": {"type": "string"},
                        "cuit": {"type": "string"}
                    },
                    "required": ["nombre"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_cliente",
                "description": "Actualiza un cliente existente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nombre": {"type": "string"},
                        "email": {"type": "string"},
                        "telefono": {"type": "string"},
                        "direccion": {"type": "string"}
                    },
                    "required": ["id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_cliente",
                "description": "Elimina un cliente por su ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"}
                    },
                    "required": ["id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_clientes",
                "description": "Obtiene lista de clientes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer"}
                    }
                }
            }
        }
    ]


def call_function(function_name: str, arguments: Dict, usuario_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Ejecuta una función basándose en su nombre y argumentos.
    
    Args:
        function_name: Nombre de la función a ejecutar
        arguments: Argumentos para la función
        usuario_id: ID del usuario para filtrar/crear registros
        
    Returns:
        Resultado de la ejecución de la función
    """
    logger.info(f"   🔧 Ejecutando función: {function_name} con argumentos: {arguments}")
    
    # Agregar usuario_id a los argumentos de creación
    if usuario_id is not None:
        if function_name in ['create_trabajo', 'create_costo', 'create_campo', 'create_cliente']:
            arguments['usuario_id'] = usuario_id
        
        # Filtrar por usuario en TODAS las operaciones (crear, leer, actualizar, eliminar)
        funciones_con_filtro = [
            'get_trabajos', 'get_costos', 'get_campos', 'get_clientes',
            'update_trabajo', 'update_costo', 'update_campo', 'update_cliente',
            'delete_trabajo', 'delete_costo', 'delete_campo', 'delete_cliente'
        ]
        if function_name in funciones_con_filtro:
            arguments['usuario_id'] = usuario_id
    
    try:
        # Funciones de creación
        if function_name == "create_trabajo":
            # El cultivo es opcional, pero si viene vacío o no viene, usar valor por defecto
            if 'cultivo' not in arguments or not arguments.get('cultivo'):
                arguments['cultivo'] = 'Sin especificar'
            
            # El estado es opcional, si no viene, usar 'Pendiente' por defecto
            if 'estado' not in arguments or not arguments.get('estado'):
                arguments['estado'] = 'Pendiente'
            
            # Procesar fecha_inicio
            if 'fecha_inicio' in arguments:
                fecha_str = str(arguments['fecha_inicio'])
                if fecha_str.lower() in ['hoy', 'today']:
                    arguments['fecha_inicio'] = date.today()
                elif fecha_str.lower() in ['mañana', 'tomorrow']:
                    from datetime import timedelta
                    arguments['fecha_inicio'] = date.today() + timedelta(days=1)
                else:
                    # Intentar parsear como YYYY-MM-DD primero
                    try:
                        if len(fecha_str) == 10 and fecha_str.count('-') == 2:
                            year, month, day = map(int, fecha_str.split('-'))
                            arguments['fecha_inicio'] = date(year, month, day)
                        else:
                            # Intentar con dateparser
                            parsed = dateparser.parse(fecha_str, languages=['es'])
                            if parsed:
                                arguments['fecha_inicio'] = parsed.date()
                            else:
                                return {"error": f"No se pudo parsear la fecha: {fecha_str}"}
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error parseando fecha '{fecha_str}': {str(e)}")
                        return {"error": f"No se pudo parsear la fecha: {fecha_str}"}
            
            # Procesar fecha_fin si existe
            if 'fecha_fin' in arguments and arguments['fecha_fin']:
                fecha_str = str(arguments['fecha_fin'])
                if fecha_str.lower() in ['hoy', 'today']:
                    arguments['fecha_fin'] = date.today()
                elif fecha_str.lower() in ['mañana', 'tomorrow']:
                    from datetime import timedelta
                    arguments['fecha_fin'] = date.today() + timedelta(days=1)
                else:
                    # Intentar parsear como YYYY-MM-DD primero
                    try:
                        if len(fecha_str) == 10 and fecha_str.count('-') == 2:
                            year, month, day = map(int, fecha_str.split('-'))
                            arguments['fecha_fin'] = date(year, month, day)
                        else:
                            # Intentar con dateparser
                            parsed = dateparser.parse(fecha_str, languages=['es'])
                            if parsed:
                                arguments['fecha_fin'] = parsed.date()
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error parseando fecha_fin '{fecha_str}': {str(e)}")
                        # Si falla, simplemente no establecer fecha_fin
                        pass
            
            # Buscar campo por nombre
            if 'campo' in arguments:
                campo = find_field_by_name(arguments['campo'], usuario_id=usuario_id)
                if campo:
                    arguments['campo_id'] = campo.id
                    del arguments['campo']
                else:
                    return {"error": f"No se encontró el campo '{arguments['campo']}'"}
            
            # Buscar tipo de trabajo por nombre
            if 'tipo_trabajo' in arguments:
                tipo = find_work_type_by_name(arguments['tipo_trabajo'])
                if tipo:
                    arguments['id_tipo_trabajo'] = tipo.id
                    del arguments['tipo_trabajo']
                else:
                    return {"error": f"No se encontró el tipo de trabajo '{arguments['tipo_trabajo']}'"}
            
            is_valid, error_msg, validated_data = validate_trabajo_data(arguments)
            if not is_valid:
                return {"error": error_msg}
            
            success, error_msg, created_data = create_trabajo(validated_data)
            if success:
                return {"success": True, "message": f"Trabajo creado exitosamente", "data": created_data}
            else:
                return {"error": error_msg}
        
        elif function_name == "create_costo":
            # Procesar fecha
            if 'fecha' in arguments:
                fecha_str = str(arguments['fecha'])
                if fecha_str.lower() in ['hoy', 'today']:
                    arguments['fecha'] = date.today()
                elif fecha_str.lower() in ['mañana', 'tomorrow']:
                    from datetime import timedelta
                    arguments['fecha'] = date.today() + timedelta(days=1)
                else:
                    # Intentar parsear como YYYY-MM-DD primero
                    try:
                        if len(fecha_str) == 10 and fecha_str.count('-') == 2:
                            year, month, day = map(int, fecha_str.split('-'))
                            arguments['fecha'] = date(year, month, day)
                        else:
                            # Intentar con dateparser
                            parsed = dateparser.parse(fecha_str, languages=['es'])
                            if parsed:
                                arguments['fecha'] = parsed.date()
                            else:
                                return {"error": f"No se pudo parsear la fecha: {fecha_str}"}
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error parseando fecha '{fecha_str}': {str(e)}")
                        return {"error": f"No se pudo parsear la fecha: {fecha_str}"}
            
            is_valid, error_msg, validated_data = validate_costo_data(arguments)
            if not is_valid:
                return {"error": error_msg}
            
            success, error_msg, created_data = create_costo(validated_data)
            if success:
                return {"success": True, "message": f"Costo creado exitosamente", "data": created_data}
            else:
                return {"error": error_msg}
        
        elif function_name == "create_campo":
            is_valid, error_msg, validated_data = validate_campo_data(arguments)
            if not is_valid:
                return {"error": error_msg}
            
            success, error_msg, created_data = create_campo(validated_data)
            if success:
                return {"success": True, "message": f"Campo creado exitosamente", "data": created_data}
            else:
                return {"error": error_msg}
        
        elif function_name == "create_cliente":
            is_valid, error_msg, validated_data = validate_cliente_data(arguments)
            if not is_valid:
                return {"error": error_msg}
            
            success, error_msg, created_data = create_cliente(validated_data)
            if success:
                return {"success": True, "message": f"Cliente creado exitosamente", "data": created_data}
            else:
                return {"error": error_msg}
        
        # Funciones de actualización
        elif function_name == "update_trabajo":
            from ..serializers import TrabajoSerializer
            
            queryset = Trabajo.objects.all()
            
            # Filtrar por usuario_id si se proporciona
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            
            # Buscar el trabajo
            trabajo = None
            
            # Si viene ID, buscar por ID
            if 'id' in arguments and arguments['id']:
                try:
                    trabajo = queryset.get(id=arguments['id'])
                except Trabajo.DoesNotExist:
                    return {"error": f"Trabajo con ID {arguments['id']} no encontrado"}
            # Si no viene ID, buscar por campo + tipo_trabajo + fecha_inicio (y opcionalmente cultivo)
            elif 'campo' in arguments and 'tipo_trabajo' in arguments:
                campo = find_field_by_name(arguments['campo'], usuario_id=usuario_id)
                if not campo:
                    return {"error": f"Campo '{arguments['campo']}' no encontrado"}
                
                tipo = find_work_type_by_name(arguments['tipo_trabajo'])
                if not tipo:
                    return {"error": f"Tipo de trabajo '{arguments['tipo_trabajo']}' no encontrado"}
                
                # Construir query
                queryset = queryset.filter(campo=campo, id_tipo_trabajo=tipo)
                
                # Si viene fecha_inicio, filtrar por fecha
                if 'fecha_inicio' in arguments and arguments['fecha_inicio']:
                    fecha_str = str(arguments['fecha_inicio'])
                    try:
                        if len(fecha_str) == 10 and fecha_str.count('-') == 2:
                            year, month, day = map(int, fecha_str.split('-'))
                            fecha_buscada = date(year, month, day)
                        else:
                            parsed = dateparser.parse(fecha_str, languages=['es'])
                            if parsed:
                                fecha_buscada = parsed.date()
                            else:
                                return {"error": f"No se pudo parsear la fecha: {fecha_str}"}
                        queryset = queryset.filter(fecha_inicio=fecha_buscada)
                    except (ValueError, TypeError) as e:
                        return {"error": f"Error parseando fecha: {str(e)}"}
                
                # Si viene cultivo, filtrar por cultivo
                if 'cultivo' in arguments and arguments['cultivo']:
                    queryset = queryset.filter(cultivo__icontains=arguments['cultivo'])
                
                # Contar resultados
                count = queryset.count()
                
                if count == 0:
                    return {"error": "No se encontró ningún trabajo que coincida con los criterios especificados"}
                elif count == 1:
                    trabajo = queryset.first()
                else:
                    # Múltiples trabajos encontrados, devolver lista para que el usuario elija
                    trabajos_list = queryset[:10]  # Limitar a 10
                    serializer = TrabajoSerializer(trabajos_list, many=True)
                    trabajos_data = []
                    for t in serializer.data:
                        trabajos_data.append({
                            'id': t.get('id'),
                            'campo': t.get('campo_nombre', 'N/A'),
                            'tipo': t.get('tipo', 'N/A'),
                            'cultivo': t.get('cultivo', 'N/A'),
                            'fecha_inicio': t.get('fecha_inicio', 'N/A'),
                            'estado': t.get('estado', 'N/A')
                        })
                    return {
                        "multiple_matches": True,
                        "message": f"Se encontraron {count} trabajos que coinciden. Por favor, especifica el ID del trabajo que deseas actualizar o proporciona más criterios (fecha o cultivo).",
                        "trabajos": trabajos_data
                    }
            else:
                return {"error": "Debes proporcionar el ID del trabajo, o campo + tipo_trabajo + fecha_inicio (y opcionalmente cultivo) para buscarlo"}
            
            # Si llegamos aquí, tenemos un trabajo único
            # Procesar campos actualizados
            update_data = {}
            for key, value in arguments.items():
                if key not in ['id', 'campo', 'tipo_trabajo', 'fecha_inicio', 'cultivo'] and value is not None:
                    if key == 'fecha_fin':
                        # Procesar fecha_fin
                        fecha_str = str(value)
                        try:
                            if len(fecha_str) == 10 and fecha_str.count('-') == 2:
                                year, month, day = map(int, fecha_str.split('-'))
                                update_data[key] = date(year, month, day)
                            elif fecha_str.lower() in ['hoy', 'today']:
                                update_data[key] = date.today()
                            elif fecha_str.lower() in ['mañana', 'tomorrow']:
                                from datetime import timedelta
                                update_data[key] = date.today() + timedelta(days=1)
                            else:
                                parsed = dateparser.parse(fecha_str, languages=['es'])
                                if parsed:
                                    update_data[key] = parsed.date()
                        except (ValueError, TypeError) as e:
                            logger.error(f"Error parseando fecha_fin '{fecha_str}': {str(e)}")
                    else:
                        update_data[key] = value
            
            serializer = TrabajoSerializer(trabajo, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return {"success": True, "message": f"Trabajo {trabajo.id} actualizado exitosamente", "data": serializer.data}
            else:
                return {"error": str(serializer.errors)}
        
        elif function_name == "update_costo":
            queryset = Costo.objects.all()
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            try:
                costo = queryset.get(id=arguments['id'])
                from ..serializers import CostoSerializer
                
                update_data = {k: v for k, v in arguments.items() if k != 'id' and v is not None}
                
                # Procesar fecha si viene
                if 'fecha' in update_data:
                    fecha_str = str(update_data['fecha'])
                    if isinstance(fecha_str, str):
                        if fecha_str.lower() in ['hoy', 'today']:
                            update_data['fecha'] = date.today()
                        elif fecha_str.lower() in ['mañana', 'tomorrow']:
                            from datetime import timedelta
                            update_data['fecha'] = date.today() + timedelta(days=1)
                        else:
                            # Intentar parsear como YYYY-MM-DD primero
                            try:
                                if len(fecha_str) == 10 and fecha_str.count('-') == 2:
                                    year, month, day = map(int, fecha_str.split('-'))
                                    update_data['fecha'] = date(year, month, day)
                                else:
                                    # Intentar con dateparser
                                    parsed = dateparser.parse(fecha_str, languages=['es'])
                                    if parsed:
                                        update_data['fecha'] = parsed.date()
                            except (ValueError, TypeError) as e:
                                logger.error(f"Error parseando fecha '{fecha_str}': {str(e)}")
                                # Si falla, mantener el valor original o usar hoy
                                update_data['fecha'] = date.today()
                
                serializer = CostoSerializer(costo, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return {"success": True, "message": f"Costo {arguments['id']} actualizado exitosamente"}
                else:
                    return {"error": str(serializer.errors)}
            except Costo.DoesNotExist:
                return {"error": f"Costo con ID {arguments['id']} no encontrado"}
        
        elif function_name == "update_campo":
            queryset = Campo.objects.all()
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            try:
                campo = queryset.get(id=arguments['id'])
                from ..serializers import CampoSerializer
                
                update_data = {k: v for k, v in arguments.items() if k != 'id' and v is not None}
                serializer = CampoSerializer(campo, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return {"success": True, "message": f"Campo {arguments['id']} actualizado exitosamente"}
                else:
                    return {"error": str(serializer.errors)}
            except Campo.DoesNotExist:
                return {"error": f"Campo con ID {arguments['id']} no encontrado"}
        
        elif function_name == "update_cliente":
            queryset = Cliente.objects.all()
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            try:
                cliente = queryset.get(id=arguments['id'])
                from ..serializers import ClienteSerializer
                
                update_data = {k: v for k, v in arguments.items() if k != 'id' and v is not None}
                serializer = ClienteSerializer(cliente, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return {"success": True, "message": f"Cliente {arguments['id']} actualizado exitosamente"}
                else:
                    return {"error": str(serializer.errors)}
            except Cliente.DoesNotExist:
                return {"error": f"Cliente con ID {arguments['id']} no encontrado"}
        
        # Funciones de eliminación
        elif function_name == "delete_trabajo":
            queryset = Trabajo.objects.all()
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            try:
                trabajo = queryset.get(id=arguments['id'])
                trabajo.delete()
                return {"success": True, "message": f"Trabajo {arguments['id']} eliminado exitosamente"}
            except Trabajo.DoesNotExist:
                return {"error": f"Trabajo con ID {arguments['id']} no encontrado"}
        
        elif function_name == "delete_costo":
            queryset = Costo.objects.all()
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            try:
                costo = queryset.get(id=arguments['id'])
                costo.delete()
                return {"success": True, "message": f"Costo {arguments['id']} eliminado exitosamente"}
            except Costo.DoesNotExist:
                return {"error": f"Costo con ID {arguments['id']} no encontrado"}
        
        elif function_name == "delete_campo":
            queryset = Campo.objects.all()
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            try:
                campo = queryset.get(id=arguments['id'])
                campo.delete()
                return {"success": True, "message": f"Campo {arguments['id']} eliminado exitosamente"}
            except Campo.DoesNotExist:
                return {"error": f"Campo con ID {arguments['id']} no encontrado"}
        
        elif function_name == "delete_cliente":
            queryset = Cliente.objects.all()
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            try:
                cliente = queryset.get(id=arguments['id'])
                cliente.delete()
                return {"success": True, "message": f"Cliente {arguments['id']} eliminado exitosamente"}
            except Cliente.DoesNotExist:
                return {"error": f"Cliente con ID {arguments['id']} no encontrado"}
        
        # Funciones de consulta
        elif function_name == "get_trabajos":
            queryset = Trabajo.objects.all()
            
            # Filtrar por usuario_id si se proporciona
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            
            if 'campo' in arguments:
                campo = find_field_by_name(arguments['campo'], usuario_id=usuario_id)
                if campo:
                    queryset = queryset.filter(campo=campo)
            
            if 'tipo_trabajo' in arguments:
                tipo = find_work_type_by_name(arguments['tipo_trabajo'])
                if tipo:
                    queryset = queryset.filter(id_tipo_trabajo=tipo)
            
            if 'cultivo' in arguments:
                queryset = queryset.filter(cultivo__icontains=arguments['cultivo'])
            
            if 'estado' in arguments:
                queryset = queryset.filter(estado=arguments['estado'])
            
            limit = arguments.get('limit', 10)
            trabajos = queryset[:limit]
            
            from ..serializers import TrabajoSerializer
            serializer = TrabajoSerializer(trabajos, many=True)
            # Convertir Decimal a float para serialización JSON
            data = []
            for item in serializer.data:
                item_clean = {}
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item_clean[key] = float(value)
                    elif isinstance(value, date):
                        item_clean[key] = value.isoformat()
                    else:
                        item_clean[key] = value
                data.append(item_clean)
            return {"success": True, "data": data, "count": len(data)}
        
        elif function_name == "get_costos":
            queryset = Costo.objects.all()
            
            # Filtrar por usuario_id si se proporciona
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            
            if 'pagado' in arguments:
                queryset = queryset.filter(pagado=arguments['pagado'])
            
            limit = arguments.get('limit', 10)
            costos = queryset[:limit]
            
            from ..serializers import CostoSerializer
            serializer = CostoSerializer(costos, many=True)
            # Convertir Decimal a float para serialización JSON
            data = []
            for item in serializer.data:
                item_clean = {}
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item_clean[key] = float(value)
                    elif isinstance(value, date):
                        item_clean[key] = value.isoformat()
                    else:
                        item_clean[key] = value
                data.append(item_clean)
            return {"success": True, "data": data, "count": len(data)}
        
        elif function_name == "get_campos":
            queryset = Campo.objects.all()
            
            # Filtrar por usuario_id si se proporciona
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            
            limit = arguments.get('limit', 10)
            campos = queryset[:limit]
            
            from ..serializers import CampoSerializer
            serializer = CampoSerializer(campos, many=True)
            # Convertir Decimal a float para serialización JSON
            data = []
            for item in serializer.data:
                item_clean = {}
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item_clean[key] = float(value)
                    elif isinstance(value, date):
                        item_clean[key] = value.isoformat()
                    else:
                        item_clean[key] = value
                data.append(item_clean)
            return {"success": True, "data": data, "count": len(data)}
        
        elif function_name == "get_clientes":
            queryset = Cliente.objects.all()
            
            # Filtrar por usuario_id si se proporciona
            if 'usuario_id' in arguments:
                queryset = queryset.filter(usuario_id=arguments['usuario_id'])
            
            limit = arguments.get('limit', 10)
            clientes = queryset[:limit]
            
            from ..serializers import ClienteSerializer
            serializer = ClienteSerializer(clientes, many=True)
            # Convertir Decimal a float para serialización JSON (aunque Cliente no tiene Decimal, por consistencia)
            data = []
            for item in serializer.data:
                item_clean = {}
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item_clean[key] = float(value)
                    elif isinstance(value, date):
                        item_clean[key] = value.isoformat()
                    else:
                        item_clean[key] = value
                data.append(item_clean)
            return {"success": True, "data": data, "count": len(data)}
        
        else:
            return {"error": f"Función '{function_name}' no implementada"}
    
    except Exception as e:
        logger.error(f"Error ejecutando función {function_name}: {str(e)}", exc_info=True)
        return {"error": f"Error ejecutando función: {str(e)}"}


def process_with_openai(message: str, usuario_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Procesa un mensaje usando OpenAI con function calling.
    
    Args:
        message: Mensaje del usuario
        usuario_id: ID del usuario (opcional)
        
    Returns:
        Tupla (éxito, respuesta)
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY no configurada")
        return False, "❌ Error: API Key de OpenAI no configurada. Contacta al administrador."
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        logger.info(f"   🤖 Enviando mensaje a OpenAI: {message[:100]}...")
        
        # Primera llamada al modelo
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente que ayuda a gestionar una empresa agrícola. Puedes crear, leer, actualizar y eliminar registros de trabajos, costos, campos y clientes. Responde siempre en español de forma clara y concisa.\n\nREGLAS CRÍTICAS:\n- SIEMPRE crea los registros que el usuario solicite, SIN IMPORTAR LA FECHA (pasada, presente o futura).\n- Las fechas futuras están PERMITIDAS y son NORMALES. Los trabajos con fechas futuras se crean con estado 'Pendiente'.\n- NUNCA rechaces crear un registro por la fecha. Si el usuario pide crear un trabajo, créalo sin importar la fecha.\n- El cultivo es opcional. Solo inclúyelo si se menciona explícitamente en el mensaje del usuario.\n- IMPORTANTE: Si el usuario usa palabras como 'completar', 'marcar como completado', 'terminar', 'finalizar', 'actualizar estado a completado', etc., NO crees un nuevo registro. En su lugar, usa update_trabajo para actualizar el trabajo existente que coincida con los criterios (campo, tipo_trabajo, fecha_inicio, y opcionalmente cultivo).\n- Si el mensaje menciona 'completar' o 'marcar como completado' y proporciona campo + tipo_trabajo + fecha (y opcionalmente cultivo), busca el trabajo existente y actualiza su estado a 'Completado'.\n- Tu función es CREAR los registros que el usuario solicite, no validar si las fechas tienen sentido."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            tools=get_openai_functions(),
            tool_choice="auto"
        )
        
        message_response = response.choices[0].message
        
        # Si el modelo quiere llamar una función
        if message_response.tool_calls:
            logger.info(f"   🔧 OpenAI quiere llamar {len(message_response.tool_calls)} función(es)")
            
            # Ejecutar todas las funciones solicitadas
            tool_results = []
            for tool_call in message_response.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                logger.info(f"   📞 Llamando función: {function_name}")
                result = call_function(function_name, arguments, usuario_id=usuario_id)
                
                # Serializar con el serializador personalizado para manejar Decimal y date
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False, default=json_serializer)
                })
            
            # Segunda llamada con los resultados
            messages = [
                {
                    "role": "system",
                    "content": "Eres un asistente que ayuda a gestionar una empresa agrícola. REGLA CRÍTICA: Las fechas futuras están COMPLETAMENTE PERMITIDAS. NO rechaces fechas futuras. NO compares fechas con la fecha actual. SIEMPRE crea los registros que el usuario solicite, SIN IMPORTAR LA FECHA (pasada, presente o futura). Si la función se ejecutó exitosamente, confirma la creación. Responde siempre en español de forma clara y concisa."
                },
                {
                    "role": "user",
                    "content": message
                },
                message_response,
                *tool_results
            ]
            
            # Verificar si hubo errores en las funciones ANTES de la segunda llamada
            has_errors = False
            error_messages = []
            for result in tool_results:
                result_data = json.loads(result['content'])
                if 'error' in result_data:
                    has_errors = True
                    error_messages.append(result_data['error'])
            
            if has_errors:
                return False, f"❌ {'; '.join(error_messages)}"
            
            # Si todas las funciones se ejecutaron exitosamente, generar respuesta de confirmación
            final_response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.3  # Reducir temperatura para respuestas más deterministas
            )
            
            response_text = final_response.choices[0].message.content
            logger.info(f"   ✅ Respuesta de OpenAI: {response_text[:100]}...")
            
            # Si la respuesta contiene palabras que indican rechazo por fecha, reemplazar con confirmación
            rejection_keywords = ['no se puede', 'no puedo', 'fecha superior', 'fecha futura no permitida', 'fecha inválida']
            if any(keyword in response_text.lower() for keyword in rejection_keywords):
                logger.warning("   ⚠️ OpenAI rechazó por fecha, generando confirmación automática")
                # Generar mensaje de confirmación basado en los resultados
                success_messages = []
                for result in tool_results:
                    result_data = json.loads(result['content'])
                    if 'success' in result_data and result_data['success']:
                        if 'data' in result_data:
                            data = result_data['data']
                            if 'id' in data:
                                success_messages.append(f"✅ {result_data.get('message', 'Registro creado exitosamente')} (ID: {data['id']})")
                            else:
                                success_messages.append(f"✅ {result_data.get('message', 'Registro creado exitosamente')}")
                
                if success_messages:
                    response_text = "\n".join(success_messages)
                else:
                    response_text = "✅ Registro creado exitosamente"
            
            return True, response_text
        
        else:
            # El modelo respondió directamente sin llamar funciones
            response_text = message_response.content
            logger.info(f"   💬 Respuesta directa de OpenAI: {response_text[:100]}...")
            return True, response_text
    
    except Exception as e:
        logger.error(f"Error procesando con OpenAI: {str(e)}", exc_info=True)
        return False, f"❌ Error al procesar con OpenAI: {str(e)}"
