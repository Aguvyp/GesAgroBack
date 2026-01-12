from rest_framework import generics
from ..models import Costo
from ..serializers import CostoSerializer
from ..utils import get_usuario_id_from_request

class CostoCreateAPIView(generics.CreateAPIView):
    queryset = Costo.objects.all()
    serializer_class = CostoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class CostoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CostoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Costo.objects.filter(usuario_id=usuario_id)
        return Costo.objects.none()

class CostoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CostoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Costo.objects.filter(usuario_id=usuario_id)
        return Costo.objects.none()