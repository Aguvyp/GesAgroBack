from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Pago
from ..serializers import PagoSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_pagos',
    summary='Obtener pagos',
    description='Obtiene una lista de pagos o un pago específico si se proporciona un pk',
    responses={200: PagoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_pagos(request, pk=None):
    """
    Obtiene una lista de pagos o un pago específico si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Pago.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        pago = get_object_or_404(queryset, pk=pk)
        serializer = PagoSerializer(pago)
        return Response(serializer.data)
    else:
        pagos = queryset
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)
