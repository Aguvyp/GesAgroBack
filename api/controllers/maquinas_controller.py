from rest_framework import generics
from ..models import Maquina
from ..serializers import MaquinaSerializer
from ..utils import get_usuario_id_from_request

class MaquinaCreateAPIView(generics.CreateAPIView):
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class MaquinaUpdateAPIView(generics.UpdateAPIView):
    serializer_class = MaquinaSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Maquina.objects.filter(usuario_id=usuario_id)
        return Maquina.objects.none()

class MaquinaDestroyAPIView(generics.DestroyAPIView):
    serializer_class = MaquinaSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Maquina.objects.filter(usuario_id=usuario_id)
        return Maquina.objects.none()