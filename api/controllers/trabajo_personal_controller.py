from rest_framework import generics
from ..models import TrabajoPersonal
from ..serializers import TrabajoPersonalSerializer
from ..utils import get_usuario_id_from_request

class TrabajoPersonalDetailView(generics.RetrieveAPIView):
    serializer_class = TrabajoPersonalSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return TrabajoPersonal.objects.filter(usuario_id=usuario_id)
        return TrabajoPersonal.objects.none()

class TrabajoPersonalUpdateView(generics.UpdateAPIView):
    serializer_class = TrabajoPersonalSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return TrabajoPersonal.objects.filter(usuario_id=usuario_id)
        return TrabajoPersonal.objects.none()

class TrabajoPersonalDestroyView(generics.DestroyAPIView):
    serializer_class = TrabajoPersonalSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return TrabajoPersonal.objects.filter(usuario_id=usuario_id)
        return TrabajoPersonal.objects.none()
