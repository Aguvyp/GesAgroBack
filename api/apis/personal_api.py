from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Personal
from ..serializers import PersonalSerializer
from ..utils import get_usuario_id_from_request

@extend_schema(
    operation_id='get_personal',
    summary='Obtener personal',
    description='Obtiene una lista de personal o un personal específico si se proporciona un pk',
    responses={200: PersonalSerializer(many=True), 404: 'Not Found'}
)
@api_view(['GET'])
def get_personal(request, pk=None):
    """
    Obtiene una lista de personal o un personal específico si se proporciona un pk.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    queryset = Personal.objects.filter(usuario_id=usuario_id)
    
    if pk is not None:
        p = get_object_or_404(queryset, pk=pk)
        serializer = PersonalSerializer(p)
        return Response(serializer.data)
    else:
        personal = queryset
        serializer = PersonalSerializer(personal, many=True)
        return Response(serializer.data)

@extend_schema(
    operation_id='validate_dni',
    summary='Validar DNI',
    description='Valida si un DNI está disponible',
    responses={200: {'type': 'object', 'properties': {'available': {'type': 'boolean'}}}}
)
@api_view(['GET'])
def validate_dni(request):
    """
    Valida si un DNI está disponible.
    """
    usuario_id = get_usuario_id_from_request(request)
    
    if not usuario_id:
        return Response(
            {"detail": "Token de acceso requerido"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    dni = request.query_params.get('dni')
    exclude_id = request.query_params.get('exclude_id')
    
    queryset = Personal.objects.filter(usuario_id=usuario_id, dni=dni)
    if exclude_id:
        queryset = queryset.exclude(id=exclude_id)
        
    return Response({"available": not queryset.exists()})
