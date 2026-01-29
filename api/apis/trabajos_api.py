from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Trabajo
from ..serializers import TrabajoSerializer
from ..utils import get_usuario_id_from_request

from django.db.models import Sum

def _add_progress_to_trabajo_data(trabajo_obj, data):
    """Auxiliar para inyectar ha_realizadas y porcentaje_progreso en el dict de datos."""
    ha_realizadas = float(trabajo_obj.trabajopersonal_set.aggregate(total=Sum('hectareas'))['total'] or 0.0)
    total_ha_campo = float(trabajo_obj.campo.hectareas) if trabajo_obj.campo and trabajo_obj.campo.hectareas else 0.0
    
    porcentaje = 0.0
    if total_ha_campo > 0:
        porcentaje = round((ha_realizadas / total_ha_campo) * 100, 2)
        
    data['ha_realizadas'] = ha_realizadas
    data['porcentaje_progreso'] = porcentaje
    return data

@extend_schema(
    operation_id='get_trabajos',
    summary='Obtener trabajos',
    description='Obtiene una lista de trabajos o un trabajo específico si se proporciona un pk',
    responses={200: TrabajoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_trabajos(request, pk=None):
    """
    Obtiene una lista de trabajos o un trabajo específico si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Trabajo.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        trabajo = get_object_or_404(queryset, pk=pk)
        serializer = TrabajoSerializer(trabajo)
        data = _add_progress_to_trabajo_data(trabajo, serializer.data)
        return Response(data)
    else:
        trabajos = queryset
        data_list = []
        for t in trabajos:
            serializer = TrabajoSerializer(t)
            t_data = _add_progress_to_trabajo_data(t, serializer.data)
            data_list.append(t_data)
        return Response(data_list)

@extend_schema(
    operation_id='get_trabajo_detalle',
    summary='Obtener detalle completo de trabajo',
    description='Obtiene el detalle completo de un trabajo incluyendo información de campo, cliente, personal y máquinas',
    responses={200: TrabajoSerializer, 404: 'Not Found'}
)
@api_view(['GET'])
def get_trabajo_detalle(request, pk):
    """
    Obtiene el detalle completo de un trabajo.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Trabajo.objects.filter(usuario_id=usuario_id)
    trabajo = get_object_or_404(queryset, pk=pk)
    serializer = TrabajoSerializer(trabajo)
    data = serializer.data
    
    # Inyectar progreso
    data = _add_progress_to_trabajo_data(trabajo, data)
    
    # Ajustes específicos para que coincida con la spec detalle/{id}
    if 'personal_detail' in data:
        data['personal'] = data.pop('personal_detail')
    return Response(data)

from ..models import TrabajoPersonal
from ..serializers import TrabajoPersonalSerializer

@extend_schema(
    operation_id='update_trabajo_personal',
    summary='Actualizar registro de personal en trabajo',
    description='Actualiza horas o hectáreas de un operario, validando que el total no supere las hectáreas del campo',
    request=TrabajoPersonalSerializer,
    responses={200: TrabajoPersonalSerializer, 400: 'Bad Request'}
)
@api_view(['PUT', 'PATCH'])
def update_trabajo_personal(request, pk):
    usuario_id = get_usuario_id_from_request(request)
    if not usuario_id:
        return Response({"detail": "Token requerido"}, status=status.HTTP_401_UNAUTHORIZED)

    # Obtenemos el registro asegurando que pertenece al usuario
    # Como TrabajoPersonal no tiene usuario_id directo en algunos modelos viejos, filtramos por Trabajo->usuario_id
    # Pero segun tu modelo TrabajoPersonal SI tiene usuario_id. Usémoslo.
    registro = get_object_or_404(TrabajoPersonal, pk=pk, usuario_id=usuario_id)
    
    serializer = TrabajoPersonalSerializer(registro, data=request.data, partial=True)
    
    if serializer.is_valid():
        # --- VALIDACIÓN DE HECTÁREAS ---
        new_hectareas = serializer.validated_data.get('hectareas')
        
        # Solo validamos si se están intentando modificar las hectáreas
        if new_hectareas is not None:
            trabajo = registro.trabajo
            
            if trabajo and trabajo.campo and trabajo.campo.hectareas:
                limit_hectareas = float(trabajo.campo.hectareas)
                
                # Sumamos lo que llevan los DEMÁS registrados en este trabajo
                current_total = trabajo.trabajopersonal_set.exclude(pk=pk).aggregate(sum=Sum('hectareas'))['sum'] or 0.0
                
                # Sumamos lo que se quiere guardar ahora
                total_maybe = float(current_total) + float(new_hectareas)
                
                if total_maybe > limit_hectareas:
                     return Response({
                        "error": f"No puedes trabajar mas hectareas totales (Actual intentado: {total_maybe}) que las que el campo tiene registradas ({limit_hectareas})"
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Guardar si pasó la validación
        serializer.save()
        return Response(serializer.data)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    operation_id='delete_trabajo_personal',
    summary='Eliminar registro de personal',
    responses={204: 'No Content'}
)
@api_view(['DELETE'])
def delete_trabajo_personal(request, pk):
    usuario_id = get_usuario_id_from_request(request)
    if not usuario_id:
        return Response({"detail": "Token requerido"}, status=status.HTTP_401_UNAUTHORIZED)
        
    registro = get_object_or_404(TrabajoPersonal, pk=pk, usuario_id=usuario_id)
    registro.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
