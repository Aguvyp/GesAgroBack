from rest_framework import generics
from ..models import Trabajo
from ..serializers import TrabajoSerializer

class TrabajoCreateAPIView(generics.CreateAPIView):
    queryset = Trabajo.objects.all()
    serializer_class = TrabajoSerializer

class TrabajoUpdateAPIView(generics.UpdateAPIView):
    queryset = Trabajo.objects.all()
    serializer_class = TrabajoSerializer

class TrabajoDestroyAPIView(generics.DestroyAPIView):
    queryset = Trabajo.objects.all()
    serializer_class = TrabajoSerializer
