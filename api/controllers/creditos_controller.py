from rest_framework import generics
from ..models import Credito
from ..serializers import CreditoSerializer

class CreditoCreateAPIView(generics.CreateAPIView):
    queryset = Credito.objects.all()
    serializer_class = CreditoSerializer

class CreditoUpdateAPIView(generics.UpdateAPIView):
    queryset = Credito.objects.all()
    serializer_class = CreditoSerializer

class CreditoDestroyAPIView(generics.DestroyAPIView):
    queryset = Credito.objects.all()
    serializer_class = CreditoSerializer
