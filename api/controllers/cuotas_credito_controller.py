from rest_framework import generics
from ..models import CuotaCredito
from ..serializers import CuotaCreditoSerializer

class CuotaCreditoCreateAPIView(generics.CreateAPIView):
    queryset = CuotaCredito.objects.all()
    serializer_class = CuotaCreditoSerializer

class CuotaCreditoUpdateAPIView(generics.UpdateAPIView):
    queryset = CuotaCredito.objects.all()
    serializer_class = CuotaCreditoSerializer

class CuotaCreditoDestroyAPIView(generics.DestroyAPIView):
    queryset = CuotaCredito.objects.all()
    serializer_class = CuotaCreditoSerializer
