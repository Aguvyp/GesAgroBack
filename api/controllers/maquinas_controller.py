from rest_framework import generics
from ..models import Maquina
from ..serializers import MaquinaSerializer

class MaquinaCreateAPIView(generics.CreateAPIView):
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer

class MaquinaUpdateAPIView(generics.UpdateAPIView):
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer

class MaquinaDestroyAPIView(generics.DestroyAPIView):
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer
