from rest_framework import generics
from ..models import Factura
from ..serializers import FacturaSerializer

class FacturaCreateAPIView(generics.CreateAPIView):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer

class FacturaUpdateAPIView(generics.UpdateAPIView):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer

class FacturaDestroyAPIView(generics.DestroyAPIView):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
