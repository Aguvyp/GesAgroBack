from rest_framework import generics
from ..models import Personal
from ..serializers import PersonalSerializer
from ..utils import get_usuario_id_from_request

class PersonalCreateAPIView(generics.CreateAPIView):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class PersonalUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PersonalSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Personal.objects.filter(usuario_id=usuario_id)
        return Personal.objects.none()

class PersonalDestroyAPIView(generics.DestroyAPIView):
    serializer_class = PersonalSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Personal.objects.filter(usuario_id=usuario_id)
        return Personal.objects.none()