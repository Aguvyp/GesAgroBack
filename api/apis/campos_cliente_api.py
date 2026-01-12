from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import CampoCliente, Campo, Cliente
from ..serializers import CampoClienteSerializer
from ..utils import get_usuario_id_from_request

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
    Filtra por usuario del campo o cliente.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Filtrar por usuario del campo o cliente
    campos_usuario = Campo.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
    clientes_usuario = Cliente.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
    
    queryset = CampoCliente.objects.filter(
        campo_id__in=campos_usuario
    ) | CampoCliente.objects.filter(
        cliente_id__in=clientes_usuario
    )
    
    if pk is not None:
        cc = get_object_or_404(queryset, pk=pk)
        serializer = CampoClienteSerializer(cc)
        return Response(serializer.data)
    else:
        cliente_id = request.query_params.get('cliente_id')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        serializer = CampoClienteSerializer(queryset, many=True)
        return Response(serializer.data)

