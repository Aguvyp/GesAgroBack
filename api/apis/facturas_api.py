from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Factura
from ..serializers import FacturaSerializer

@extend_schema(
    operation_id='get_facturas',
    summary='Obtener facturas',
    description='Obtiene una lista de facturas o una factura específica si se proporciona un pk',
    responses={200: FacturaSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_facturas(request, pk=None):
    """
    Obtiene una lista de facturas o una factura específica si se proporciona un pk.
    """
    if pk is not None:
        factura = get_object_or_404(Factura, pk=pk)
        serializer = FacturaSerializer(factura)
        return Response(serializer.data)
    else:
        facturas = Factura.objects.all()
        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data)
