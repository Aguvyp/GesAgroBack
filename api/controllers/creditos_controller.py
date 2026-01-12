from rest_framework import generics
from ..models import Credito
from ..serializers import CreditoSerializer
from ..utils import get_usuario_id_from_request

class CreditoCreateAPIView(generics.CreateAPIView):
    queryset = Credito.objects.all()
    serializer_class = CreditoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class CreditoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CreditoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Credito.objects.filter(usuario_id=usuario_id)
        return Credito.objects.none()

class CreditoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CreditoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Credito.objects.filter(usuario_id=usuario_id)
        return Credito.objects.none()