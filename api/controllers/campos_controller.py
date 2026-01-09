from rest_framework import generics
from ..models import Campo
from ..serializers import CampoSerializer

class CampoCreateAPIView(generics.CreateAPIView):
    queryset = Campo.objects.all()
    serializer_class = CampoSerializer

class CampoUpdateAPIView(generics.UpdateAPIView):
    queryset = Campo.objects.all()
    serializer_class = CampoSerializer

class CampoDestroyAPIView(generics.DestroyAPIView):
    queryset = Campo.objects.all()
    serializer_class = CampoSerializer
