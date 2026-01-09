from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Usuario
from ..serializers import UsuarioSerializer

@extend_schema(
    operation_id='get_usuarios',
    summary='Obtener usuarios',
    description='Obtiene una lista de usuarios o un usuario específico si se proporciona un pk',
    responses={200: UsuarioSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_usuarios(request, pk=None):
    """
    Obtiene una lista de usuarios o un usuario específico si se proporciona un pk.
    """
    if pk is not None:
        usuario = get_object_or_404(Usuario, pk=pk)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)
    else:
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 100))
        usuarios = Usuario.objects.all()[skip:skip+limit]
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
