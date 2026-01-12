from rest_framework import generics
from ..models import Pago
from ..serializers import PagoSerializer
from ..utils import get_usuario_id_from_request

class PagoCreateAPIView(generics.CreateAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class PagoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PagoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Pago.objects.filter(usuario_id=usuario_id)
        return Pago.objects.none()

class PagoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = PagoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Pago.objects.filter(usuario_id=usuario_id)
        return Pago.objects.none()