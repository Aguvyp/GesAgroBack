from rest_framework import generics
from ..models import Factura
from ..serializers import FacturaSerializer
from ..utils import get_usuario_id_from_request

class FacturaCreateAPIView(generics.CreateAPIView):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class FacturaUpdateAPIView(generics.UpdateAPIView):
    serializer_class = FacturaSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Factura.objects.filter(usuario_id=usuario_id)
        return Factura.objects.none()

class FacturaDestroyAPIView(generics.DestroyAPIView):
    serializer_class = FacturaSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Factura.objects.filter(usuario_id=usuario_id)
        return Factura.objects.none()