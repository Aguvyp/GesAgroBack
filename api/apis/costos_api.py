from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Costo
from ..serializers import CostoSerializer

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
    if pk is not None:
        costo = get_object_or_404(Costo, pk=pk)
        serializer = CostoSerializer(costo)
        return Response(serializer.data)
    else:
        costos = Costo.objects.all()
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
    costos = Costo.objects.filter(pagado=True)
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
    costos = Costo.objects.filter(pagado=False)
    serializer = CostoSerializer(costos, many=True)
    return Response(serializer.data)
