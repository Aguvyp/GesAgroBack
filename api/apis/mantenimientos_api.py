from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Mantenimiento
from ..serializers import MantenimientoSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_mantenimientos',
    summary='Obtener mantenimientos',
    description='Obtiene una lista de mantenimientos o un mantenimiento específico si se proporciona un pk',
    responses={200: MantenimientoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_mantenimientos(request, pk=None):
    """
    Obtiene una lista de mantenimientos o un mantenimiento específico si se proporciona un pk.
    Requerimiento específico: devolver [] en caso de error.
    """
    try:
        usuario_id = get_usuario_id_from_request(request)
        
        if not usuario_id:
            return Response(
                {"detail": "Token de acceso requerido"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = Mantenimiento.objects.filter(usuario_id=usuario_id)
        
        if pk is not None:
            mantenimiento = get_object_or_404(queryset, pk=pk)
            serializer = MantenimientoSerializer(mantenimiento)
            return Response(serializer.data)
        else:
            mantenimientos = queryset
            serializer = MantenimientoSerializer(mantenimientos, many=True)
            return Response(serializer.data)
    except Exception:
        return Response([])  # Requerimiento específico: devolver [] en caso de error
