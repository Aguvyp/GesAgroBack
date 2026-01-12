from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Campo
from ..serializers import CampoSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_campos',
    summary='Obtener campos',
    description='Obtiene una lista de campos o un campo específico si se proporciona un pk',
    responses={200: CampoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_campos(request, pk=None):
    """
    Obtiene una lista de campos o un campo específico si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Campo.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        campo = get_object_or_404(queryset, pk=pk)
        serializer = CampoSerializer(campo)
        return Response(serializer.data)
    else:
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 100))
        campos = queryset[skip:skip+limit]
        serializer = CampoSerializer(campos, many=True)
        return Response(serializer.data)
