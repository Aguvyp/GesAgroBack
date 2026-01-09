from rest_framework import generics
from ..models import Mantenimiento
from ..serializers import MantenimientoSerializer

class MantenimientoCreateAPIView(generics.CreateAPIView):
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer

class MantenimientoUpdateAPIView(generics.UpdateAPIView):
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer

class MantenimientoDestroyAPIView(generics.DestroyAPIView):
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer
