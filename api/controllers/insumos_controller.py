from rest_framework import generics
from ..models import Insumo
from ..serializers import InsumoSerializer
from ..utils import get_usuario_id_from_request

class InsumoCreateAPIView(generics.CreateAPIView):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class InsumoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = InsumoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Insumo.objects.filter(usuario_id=usuario_id)
        return Insumo.objects.none()

class InsumoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = InsumoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Insumo.objects.filter(usuario_id=usuario_id)
        return Insumo.objects.none()