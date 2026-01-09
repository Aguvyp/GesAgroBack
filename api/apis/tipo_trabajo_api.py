from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import TipoTrabajo
from ..serializers import TipoTrabajoSerializer

@extend_schema(
    operation_id='get_tipo_trabajo',
    summary='Obtener tipos de trabajo',
    description='Obtiene una lista de tipos de trabajo o un tipo específico si se proporciona un pk',
    responses={200: TipoTrabajoSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_tipo_trabajo(request, pk=None):
    """
    Obtiene una lista de tipos de trabajo o un tipo específico si se proporciona un pk.
    """
    if pk is not None:
        tipo = get_object_or_404(TipoTrabajo, pk=pk)
        serializer = TipoTrabajoSerializer(tipo)
        return Response(serializer.data)
    else:
        tipos = TipoTrabajo.objects.all()
        serializer = TipoTrabajoSerializer(tipos, many=True)
        return Response(serializer.data)
