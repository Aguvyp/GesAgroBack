from rest_framework import generics, status
from rest_framework.response import Response
from ..models import Trabajo
from ..serializers import TrabajoSerializer
from ..utils import get_usuario_id_from_request

class TrabajoCreateAPIView(generics.CreateAPIView):
    queryset = Trabajo.objects.all()
    serializer_class = TrabajoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class TrabajoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = TrabajoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Trabajo.objects.filter(usuario_id=usuario_id)
        return Trabajo.objects.none()

class TrabajoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = TrabajoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Trabajo.objects.filter(usuario_id=usuario_id)
        return Trabajo.objects.none()