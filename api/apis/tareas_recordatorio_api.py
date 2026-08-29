from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import TareaRecordatorio
from ..serializers import TareaRecordatorioSerializer
from ..utils import get_usuario_id_from_request


@extend_schema(
    operation_id='get_tareas_recordatorio',
    summary='Obtener tareas recordatorio',
    description='Obtiene una lista de tareas recordatorio del usuario autenticado o una tarea específica si se proporciona un pk.',
    responses={200: TareaRecordatorioSerializer(many=True), 404: 'Not Found'},
)
@api_view(['GET'])
def get_tareas_recordatorio(request, pk=None):
    usuario_id = get_usuario_id_from_request(request)

    if not usuario_id:
        return Response(
            {'detail': 'Token de acceso requerido'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    queryset = TareaRecordatorio.objects.filter(usuario_id=usuario_id)

    if pk is not None:
        tarea = get_object_or_404(queryset, pk=pk)
        serializer = TareaRecordatorioSerializer(tarea)
        return Response(serializer.data)

    serializer = TareaRecordatorioSerializer(queryset, many=True)
    return Response(serializer.data)
