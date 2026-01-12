from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Movimiento
from ..serializers import MovimientoSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_movimientos',
    summary='Obtener movimientos',
    description='Obtiene una lista de movimientos o un movimiento específico si se proporciona un pk',
    responses={200: MovimientoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_movimientos(request, pk=None):
    """
    Obtiene una lista de movimientos o un movimiento específico si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Movimiento.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        movimiento = get_object_or_404(queryset, pk=pk)
        serializer = MovimientoSerializer(movimiento)
        return Response(serializer.data)
    else:
        movimientos = queryset
        serializer = MovimientoSerializer(movimientos, many=True)
        return Response(serializer.data)
