from rest_framework import generics
from ..models import Movimiento
from ..serializers import MovimientoSerializer

class MovimientoCreateAPIView(generics.CreateAPIView):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer

class MovimientoUpdateAPIView(generics.UpdateAPIView):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer

class MovimientoDestroyAPIView(generics.DestroyAPIView):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
