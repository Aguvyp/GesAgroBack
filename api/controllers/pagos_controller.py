from rest_framework import generics
from ..models import Pago
from ..serializers import PagoSerializer

class PagoCreateAPIView(generics.CreateAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class PagoUpdateAPIView(generics.UpdateAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class PagoDestroyAPIView(generics.DestroyAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
