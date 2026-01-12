from rest_framework import generics
from ..models import Campo
from ..serializers import CampoSerializer
from ..utils import get_usuario_id_from_request

class CampoCreateAPIView(generics.CreateAPIView):
    queryset = Campo.objects.all()
    serializer_class = CampoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class CampoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CampoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Campo.objects.filter(usuario_id=usuario_id)
        return Campo.objects.none()

class CampoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CampoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Campo.objects.filter(usuario_id=usuario_id)
        return Campo.objects.none()