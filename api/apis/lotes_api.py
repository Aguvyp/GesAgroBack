from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Lote
from ..serializers import LoteSerializer
from ..utils import get_usuario_id_from_request


@extend_schema(
    operation_id='get_lotes',
    summary='Obtener lotes',
    description='Lista lotes del usuario, opcionalmente filtrados por campo_id, o devuelve un lote por pk',
    responses={200: LoteSerializer(many=True), 404: 'Not Found'},
)
@api_view(['GET'])
def get_lotes(request, pk=None):
    usuario_id = get_usuario_id_from_request(request)

    if not usuario_id:
        return Response(
            {'detail': 'Token de acceso requerido'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    queryset = Lote.objects.filter(usuario_id=usuario_id).select_related('campo')
    campo_id = request.query_params.get('campo_id')
    if campo_id:
        queryset = queryset.filter(campo_id=campo_id)

    if pk is not None:
        lote = get_object_or_404(queryset, pk=pk)
        serializer = LoteSerializer(lote)
        return Response(serializer.data)

    skip = int(request.query_params.get('skip', 0))
    limit = int(request.query_params.get('limit', 100))
    lotes = queryset.order_by('campo__nombre', 'nombre')[skip:skip + limit]
    serializer = LoteSerializer(lotes, many=True)
    return Response(serializer.data)
