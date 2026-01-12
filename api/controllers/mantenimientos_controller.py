from rest_framework import generics
from ..models import Mantenimiento
from ..serializers import MantenimientoSerializer
from ..utils import get_usuario_id_from_request

class MantenimientoCreateAPIView(generics.CreateAPIView):
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class MantenimientoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = MantenimientoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Mantenimiento.objects.filter(usuario_id=usuario_id)
        return Mantenimiento.objects.none()

class MantenimientoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = MantenimientoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Mantenimiento.objects.filter(usuario_id=usuario_id)
        return Mantenimiento.objects.none()