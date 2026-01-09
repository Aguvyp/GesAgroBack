from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Movimiento
from ..serializers import MovimientoSerializer

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
    if pk is not None:
        movimiento = get_object_or_404(Movimiento, pk=pk)
        serializer = MovimientoSerializer(movimiento)
        return Response(serializer.data)
    else:
        movimientos = Movimiento.objects.all()
        serializer = MovimientoSerializer(movimientos, many=True)
        return Response(serializer.data)
