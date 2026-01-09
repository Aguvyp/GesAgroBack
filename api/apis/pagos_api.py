from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Pago
from ..serializers import PagoSerializer

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
    if pk is not None:
        pago = get_object_or_404(Pago, pk=pk)
        serializer = PagoSerializer(pago)
        return Response(serializer.data)
    else:
        pagos = Pago.objects.all()
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)
