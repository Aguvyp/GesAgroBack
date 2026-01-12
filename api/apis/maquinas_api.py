from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Maquina
from ..serializers import MaquinaSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_maquinas',
    summary='Obtener máquinas',
    description='Obtiene una lista de máquinas o una máquina específica si se proporciona un pk',
    responses={200: MaquinaSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_maquinas(request, pk=None):
    """
    Obtiene una lista de máquinas o una máquina específica si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Maquina.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        maquina = get_object_or_404(queryset, pk=pk)
        serializer = MaquinaSerializer(maquina)
        return Response(serializer.data)
    else:
        maquinas = queryset
        serializer = MaquinaSerializer(maquinas, many=True)
        return Response(serializer.data)
