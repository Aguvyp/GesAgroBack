from rest_framework import generics
from ..models import Insumo
from ..serializers import InsumoSerializer

class InsumoCreateAPIView(generics.CreateAPIView):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

class InsumoUpdateAPIView(generics.UpdateAPIView):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

class InsumoDestroyAPIView(generics.DestroyAPIView):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
