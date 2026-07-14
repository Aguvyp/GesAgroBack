"""Lógica del agente OpenCode: funciones CRUD y utilidades para el LLM gratuito."""
import json
import logging
from decimal import Decimal
from datetime import date
from typing import Any, Dict, List, Optional

from django.db.models import QuerySet
from ..models import (
    Trabajo, Costo, Campo, Cliente, Personal, TrabajoPersonal, TipoTrabajo
)
from ..serializers import (
    TrabajoSerializer, CostoSerializer, CampoSerializer, ClienteSerializer, PersonalSerializer
)
from .crud_creator import (
    create_trabajo, create_costo, create_campo, create_cliente
)
from .crud_validator import (
    validate_trabajo_data, validate_costo_data, validate_campo_data, validate_cliente_data,
    find_field_by_name, find_work_type_by_name
)

logger = logging.getLogger(__name__)


def json_serializer(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


FUNCTION_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "create_trabajo",
        "description": "Crea un trabajo nuevo y lo asocia al usuario que pidió la acción",
        "parameters": ["tipo_trabajo", "campo", "fecha_inicio"],
    },
    {
        "name": "update_trabajo",
        "description": "Actualiza un trabajo existente por ID o contexto (campo + tipo + fecha)",
        "parameters": ["id", "campo", "tipo_trabajo", "estado", "fecha_fin"]
    },
    {
        "name": "delete_trabajo",
        "description": "Elimina un trabajo por su ID",
        "parameters": ["id"]
    },
    {
        "name": "get_trabajos",
        "description": "Lista trabajos filtrando por usuario/campo/tipo/estado",
        "parameters": ["campo", "tipo_trabajo", "estado", "limit"]
    },
    *[
        {"name": name, "description": desc, "parameters": params}
        for name, desc, params in [
            ("create_costo", "Registra un nuevo costo", ["monto", "fecha", "destinatario"]),
            ("update_costo", "Modifica un costo existente", ["id", "monto", "fecha", "pagado"]),
            ("delete_costo", "Elimina un costo", ["id"]),
            ("get_costos", "Enumera costos del usuario", ["pagado", "limit"]),
            ("create_campo", "Crea un campo (propio o de cliente)", ["nombre", "propio", "cliente_id", "hectareas"]),
            ("update_campo", "Actualiza un campo", ["id", "nombre", "hectareas"]),
            ("delete_campo", "Elimina un campo", ["id"]),
            ("get_campos", "Lista los campos del usuario", ["limit"]),
            ("create_cliente", "Registra un cliente nuevo", ["nombre", "cuit"]),
            ("update_cliente", "Actualiza un cliente", ["id", "email", "telefono"]),
            ("delete_cliente", "Elimina un cliente", ["id"]),
            ("get_clientes", "Lista los clientes", ["limit"]),
            ("create_personal", "Agrega personal" , ["nombre", "dni", "telefono"]),
            ("update_personal", "Actualiza personal", ["id", "nombre", "dni"]),
            ("delete_personal", "Elimina personal", ["id"]),
            ("get_personal", "Lista el personal", ["limit"]),
            ("assign_personal_to_trabajo", "Asigna personal a un trabajo", ["trabajo_id", "personal_id"]),
            ("remove_personal_from_trabajo", "Desasigna personal", ["trabajo_id", "personal_id"]),
            ("get_trabajo_personal", "Consulta personal asignado", ["trabajo_id"]),
        ]
    ]
]


def _serialize_queryset(queryset: QuerySet, serializer_class):
    serializer = serializer_class(queryset, many=True)
    data = []
    for row in serializer.data:
        row_clean = {}
        for key, value in row.items():
            if isinstance(value, Decimal):
                row_clean[key] = float(value)
            elif isinstance(value, date):
                row_clean[key] = value.isoformat()
            else:
                row_clean[key] = value
        data.append(row_clean)
    return data


def call_function(function_name: str, arguments: Dict[str, Any], usuario_id: Optional[int] = None) -> Dict[str, Any]:
    data = {k: v for k, v in arguments.items() if v is not None}
    if usuario_id is not None:
        data['usuario_id'] = usuario_id

    logger.info(f"Ejecutando función {function_name} con {data}")

    try:
        if function_name == "create_trabajo":
            is_valid, error_msg, validated = validate_trabajo_data(data)
            if not is_valid:
                return {"error": error_msg}
            success, error_msg, payload = create_trabajo(validated)
            return {"success": success, "message": error_msg if error_msg else "Trabajo creado", "data": payload}

        if function_name == "create_costo":
            is_valid, error_msg, validated = validate_costo_data(data)
            if not is_valid:
                return {"error": error_msg}
            success, error_msg, payload = create_costo(validated)
            return {"success": success, "message": error_msg if error_msg else "Costo creado", "data": payload}

        if function_name == "create_campo":
            is_valid, error_msg, validated = validate_campo_data(data)
            if not is_valid:
                return {"error": error_msg}
            success, error_msg, payload = create_campo(validated)
            return {"success": success, "message": error_msg if error_msg else "Campo creado", "data": payload}

        if function_name == "create_cliente":
            is_valid, error_msg, validated = validate_cliente_data(data)
            if not is_valid:
                return {"error": error_msg}
            success, error_msg, payload = create_cliente(validated)
            return {"success": success, "message": error_msg if error_msg else "Cliente creado", "data": payload}

        if function_name == "create_personal":
            if 'nombre' not in data or not data['nombre']:
                return {"error": "El nombre es obligatorio para crear personal"}
            personal_data = {
                'nombre': data['nombre'],
                'usuario_id': data.get('usuario_id')
            }
            if 'dni' in data:
                personal_data['dni'] = data['dni']
            if 'telefono' in data:
                personal_data['telefono'] = data['telefono']
            serializer = PersonalSerializer(data=personal_data)
            if serializer.is_valid():
                personal = serializer.save()
                return {
                    "success": True,
                    "message": f"Personal '{personal.nombre}' creado",
                    "data": {
                        'id': personal.id,
                        'nombre': personal.nombre,
                        'dni': personal.dni,
                        'telefono': personal.telefono
                    }
                }
            return {"error": json.dumps(serializer.errors)}

        if function_name == "get_trabajos":
            queryset = Trabajo.objects.all()
            if data.get('usuario_id'):
                queryset = queryset.filter(usuario_id=data['usuario_id'])
            if 'campo' in data:
                campo = find_field_by_name(data['campo'], usuario_id=data.get('usuario_id'))
                if campo:
                    queryset = queryset.filter(campo=campo)
            if 'tipo_trabajo' in data:
                tipo = find_work_type_by_name(data['tipo_trabajo'])
                if tipo:
                    queryset = queryset.filter(id_tipo_trabajo=tipo)
            if 'estado' in data:
                queryset = queryset.filter(estado=data['estado'])
            limit = data.get('limit', 10)
            trabajos = queryset[:limit]
            return {"success": True, "data": _serialize_queryset(trabajos, TrabajoSerializer), "count": len(trabajos)}

        if function_name == "get_costos":
            queryset = Costo.objects.all()
            if data.get('usuario_id'):
                queryset = queryset.filter(usuario_id=data['usuario_id'])
            if 'pagado' in data:
                queryset = queryset.filter(pagado=data['pagado'])
            limit = data.get('limit', 10)
            costos = queryset[:limit]
            return {"success": True, "data": _serialize_queryset(costos, CostoSerializer), "count": len(costos)}

        if function_name == "get_campos":
            queryset = Campo.objects.all()
            if data.get('usuario_id'):
                queryset = queryset.filter(usuario_id=data['usuario_id'])
            limit = data.get('limit', 10)
            campos = queryset[:limit]
            return {"success": True, "data": _serialize_queryset(campos, CampoSerializer), "count": len(campos)}

        if function_name == "get_clientes":
            queryset = Cliente.objects.all()
            if data.get('usuario_id'):
                queryset = queryset.filter(usuario_id=data['usuario_id'])
            limit = data.get('limit', 50)
            clientes = queryset[:limit]
            return {"success": True, "data": _serialize_queryset(clientes, ClienteSerializer), "count": len(clientes)}

        if function_name == "get_personal":
            queryset = Personal.objects.all()
            if data.get('usuario_id'):
                queryset = queryset.filter(usuario_id=data['usuario_id'])
            limit = data.get('limit', 50)
            personal_list = queryset[:limit]
            return {"success": True, "data": _serialize_queryset(personal_list, PersonalSerializer), "count": len(personal_list)}

        if function_name == "assign_personal_to_trabajo":
            trabajo_id = data.get('trabajo_id')
            personal_id = data.get('personal_id')
            if not trabajo_id or not personal_id:
                return {"error": "trabajo_id y personal_id son necesarios"}
            from django.shortcuts import get_object_or_404
            trabajo = get_object_or_404(Trabajo, id=trabajo_id, usuario_id=data.get('usuario_id'))
            personal = get_object_or_404(Personal, id=personal_id, usuario_id=data.get('usuario_id'))
            existing = TrabajoPersonal.objects.filter(trabajo=trabajo, personal=personal).first()
            if existing:
                return {"success": True, "message": "El personal ya estaba asignado", "data": {"trabajo_id": trabajo_id, "personal_id": personal_id}}
            assignment = TrabajoPersonal.objects.create(
                trabajo=trabajo,
                personal=personal,
                hectareas=data.get('hectareas'),
                horas_trabajadas=data.get('horas_trabajadas')
            )
            return {"success": True, "message": "Personal asignado", "data": {'id': assignment.id}}

        if function_name == "remove_personal_from_trabajo":
            trabajo_id = data.get('trabajo_id')
            personal_id = data.get('personal_id')
            if not trabajo_id or not personal_id:
                return {"error": "trabajo_id y personal_id son necesarios"}
            assignment = TrabajoPersonal.objects.filter(trabajo_id=trabajo_id, personal_id=personal_id).first()
            if not assignment:
                return {"error": "No existe la asignación indicada"}
            assignment.delete()
            return {"success": True, "message": "Personal desasignado"}

        if function_name == "get_trabajo_personal":
            trabajo_id = data.get('trabajo_id')
            if not trabajo_id:
                return {"error": "trabajo_id es requerido"}
            assignments = TrabajoPersonal.objects.filter(trabajo_id=trabajo_id)
            result = []
            for a in assignments:
                result.append({
                    'personal_id': a.personal.id if a.personal else None,
                    'nombre': a.personal.nombre if a.personal else None,
                    'hectareas': float(a.hectareas) if a.hectareas else 0,
                    'horas_trabajadas': float(a.horas_trabajadas) if a.horas_trabajadas else 0,
                })
            return {"success": True, "data": result}

        return {"error": f"Función {function_name} no reconocida"}

    except Exception as exc:
        logger.error(f"Error ejecutando {function_name}: {str(exc)}", exc_info=True)
        return {"error": str(exc)}
