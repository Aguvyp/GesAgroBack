from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Insumo
from ..serializers import InsumoSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_insumos',
    summary='Obtener insumos',
    description='Obtiene una lista de insumos o un insumo específico si se proporciona un pk',
    responses={200: InsumoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_insumos(request, pk=None):
    """
    Obtiene una lista de insumos o un insumo específico si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Insumo.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        insumo = get_object_or_404(queryset, pk=pk)
        serializer = InsumoSerializer(insumo)
        return Response(serializer.data)
    else:
        insumos = queryset
        serializer = InsumoSerializer(insumos, many=True)
        return Response(serializer.data)
