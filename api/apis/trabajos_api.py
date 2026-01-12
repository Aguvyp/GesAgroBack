from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Trabajo
from ..serializers import TrabajoSerializer
from ..utils import get_usuario_id_from_request

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
        return Response(serializer.data)
    else:
        trabajos = queryset
        serializer = TrabajoSerializer(trabajos, many=True)
        return Response(serializer.data)

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
    
    # Ajustes específicos para que coincida con la spec detalle/{id}
    if 'personal_detail' in data:
        data['personal'] = data.pop('personal_detail')
    return Response(data)
