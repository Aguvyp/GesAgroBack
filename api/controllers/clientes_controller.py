from rest_framework import generics
from ..models import Cliente
from ..serializers import ClienteSerializer
from ..utils import get_usuario_id_from_request

class ClienteCreateAPIView(generics.CreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class ClienteUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ClienteSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Cliente.objects.filter(usuario_id=usuario_id)
        return Cliente.objects.none()

class ClienteDestroyAPIView(generics.DestroyAPIView):
    serializer_class = ClienteSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Cliente.objects.filter(usuario_id=usuario_id)
        return Cliente.objects.none()