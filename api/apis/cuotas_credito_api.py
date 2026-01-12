from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import CuotaCredito, Credito
from ..serializers import CuotaCreditoSerializer
from ..utils import get_usuario_id_from_request

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
    Filtra por usuario del crédito padre.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Filtrar cuotas por usuario del crédito padre
    creditos_usuario = Credito.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
    queryset = CuotaCredito.objects.filter(credito_id__in=creditos_usuario)
    
    if pk is not None:
        cuota = get_object_or_404(queryset, pk=pk)
        serializer = CuotaCreditoSerializer(cuota)
        return Response(serializer.data)
    else:
        cuotas = queryset
        serializer = CuotaCreditoSerializer(cuotas, many=True)
        return Response(serializer.data)
