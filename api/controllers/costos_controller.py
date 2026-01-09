from rest_framework import generics
from ..models import Costo
from ..serializers import CostoSerializer

class CostoCreateAPIView(generics.CreateAPIView):
    queryset = Costo.objects.all()
    serializer_class = CostoSerializer

class CostoUpdateAPIView(generics.UpdateAPIView):
    queryset = Costo.objects.all()
    serializer_class = CostoSerializer

class CostoDestroyAPIView(generics.DestroyAPIView):
    queryset = Costo.objects.all()
    serializer_class = CostoSerializer
