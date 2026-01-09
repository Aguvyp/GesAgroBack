from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Cliente
from ..serializers import ClienteSerializer

@extend_schema(
    operation_id='get_clientes',
    summary='Obtener clientes',
    description='Obtiene una lista de clientes o un cliente específico si se proporciona un pk',
    responses={200: ClienteSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_clientes(request, pk=None):
    """
    Obtiene una lista de clientes o un cliente específico si se proporciona un pk.
    """
    if pk is not None:
        cliente = get_object_or_404(Cliente, pk=pk)
        serializer = ClienteSerializer(cliente)
        return Response(serializer.data)
    else:
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)
