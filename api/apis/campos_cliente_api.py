from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import CampoCliente
from ..serializers import CampoClienteSerializer

@extend_schema(
    operation_id='get_campos_cliente',
    summary='Obtener asignaciones campo-cliente',
    description='Obtiene una lista de asignaciones campo-cliente o una asignación específica si se proporciona un pk',
    responses={200: CampoClienteSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_campos_cliente(request, pk=None):
    """
    Obtiene una lista de asignaciones campo-cliente o una asignación específica si se proporciona un pk.
    """
    if pk is not None:
        cc = get_object_or_404(CampoCliente, pk=pk)
        serializer = CampoClienteSerializer(cc)
        return Response(serializer.data)
    else:
        cliente_id = request.query_params.get('cliente_id')
        queryset = CampoCliente.objects.all()
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        serializer = CampoClienteSerializer(queryset, many=True)
        return Response(serializer.data)

