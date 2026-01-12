from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import CampoCliente, Campo, Cliente
from ..serializers import CampoClienteSerializer
from ..utils import get_usuario_id_from_request

class CampoClienteCreateAPIView(generics.CreateAPIView):
    queryset = CampoCliente.objects.all()
    serializer_class = CampoClienteSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class CampoClienteUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CampoClienteSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            campos_usuario = Campo.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
            clientes_usuario = Cliente.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
            return CampoCliente.objects.filter(
                campo_id__in=campos_usuario
            ) | CampoCliente.objects.filter(
                cliente_id__in=clientes_usuario
            )
        return CampoCliente.objects.none()

class CampoClienteDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CampoClienteSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            campos_usuario = Campo.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
            clientes_usuario = Cliente.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
            return CampoCliente.objects.filter(
                campo_id__in=campos_usuario
            ) | CampoCliente.objects.filter(
                cliente_id__in=clientes_usuario
            )
        return CampoCliente.objects.none()

class CampoClienteDesactivarView(APIView):
    def patch(self, request, pk):
        usuario_id = get_usuario_id_from_request(request)
        
        if not usuario_id:
            return Response(
                {"detail": "Token de acceso requerido"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        campos_usuario = Campo.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
        clientes_usuario = Cliente.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
        queryset = CampoCliente.objects.filter(
            campo_id__in=campos_usuario
        ) | CampoCliente.objects.filter(
            cliente_id__in=clientes_usuario
        )
        
        cc = get_object_or_404(queryset, pk=pk)
        cc.activo = False
        cc.save()
        serializer = CampoClienteSerializer(cc)
        return Response(serializer.data)
