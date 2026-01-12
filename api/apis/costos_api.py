from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Costo
from ..serializers import CostoSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_costos',
    summary='Obtener costos',
    description='Obtiene una lista de costos o un costo específico si se proporciona un pk',
    responses={200: CostoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_costos(request, pk=None):
    """
    Obtiene una lista de costos o un costo específico si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Costo.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        costo = get_object_or_404(queryset, pk=pk)
        serializer = CostoSerializer(costo)
        return Response(serializer.data)
    else:
        costos = queryset
        serializer = CostoSerializer(costos, many=True)
        return Response(serializer.data)

@extend_schema(
    operation_id='get_costos_pagados',
    summary='Obtener costos pagados',
    description='Obtiene una lista de costos pagados',
    responses={200: CostoSerializer(many=True)}
)
@api_view(['GET'])
def get_costos_pagados(request):
    """
    Obtiene una lista de costos pagados.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    costos = Costo.objects.filter(usuario_id=usuario_id, pagado=True)
    serializer = CostoSerializer(costos, many=True)
    return Response(serializer.data)

@extend_schema(
    operation_id='get_costos_pendientes',
    summary='Obtener costos pendientes',
    description='Obtiene una lista de costos pendientes',
    responses={200: CostoSerializer(many=True)}
)
@api_view(['GET'])
def get_costos_pendientes(request):
    """
    Obtiene una lista de costos pendientes.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    costos = Costo.objects.filter(usuario_id=usuario_id, pagado=False)
    serializer = CostoSerializer(costos, many=True)
    return Response(serializer.data)
