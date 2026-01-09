from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import CuotaCredito
from ..serializers import CuotaCreditoSerializer

@extend_schema(
    operation_id='get_cuotas_credito',
    summary='Obtener cuotas de crédito',
    description='Obtiene una lista de cuotas de crédito o una cuota específica si se proporciona un pk',
    responses={200: CuotaCreditoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_cuotas_credito(request, pk=None):
    """
    Obtiene una lista de cuotas de crédito o una cuota específica si se proporciona un pk.
    """
    if pk is not None:
        cuota = get_object_or_404(CuotaCredito, pk=pk)
        serializer = CuotaCreditoSerializer(cuota)
        return Response(serializer.data)
    else:
        cuotas = CuotaCredito.objects.all()
        serializer = CuotaCreditoSerializer(cuotas, many=True)
        return Response(serializer.data)
