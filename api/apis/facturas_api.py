from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Factura
from ..serializers import FacturaSerializer
from ..utils import get_usuario_id_from_request

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
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Factura.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        factura = get_object_or_404(queryset, pk=pk)
        serializer = FacturaSerializer(factura)
        return Response(serializer.data)
    else:
        facturas = queryset
        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data)
