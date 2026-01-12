from rest_framework import generics
from ..models import Movimiento
from ..serializers import MovimientoSerializer
from ..utils import get_usuario_id_from_request

class MovimientoCreateAPIView(generics.CreateAPIView):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class MovimientoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = MovimientoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Movimiento.objects.filter(usuario_id=usuario_id)
        return Movimiento.objects.none()

class MovimientoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = MovimientoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Movimiento.objects.filter(usuario_id=usuario_id)
        return Movimiento.objects.none()