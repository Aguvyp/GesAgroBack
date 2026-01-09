from rest_framework import generics
from ..models import TipoTrabajo
from ..serializers import TipoTrabajoSerializer

class TipoTrabajoCreateAPIView(generics.CreateAPIView):
    queryset = TipoTrabajo.objects.all()
    serializer_class = TipoTrabajoSerializer

class TipoTrabajoUpdateAPIView(generics.UpdateAPIView):
    queryset = TipoTrabajo.objects.all()
    serializer_class = TipoTrabajoSerializer

class TipoTrabajoDestroyAPIView(generics.DestroyAPIView):
    queryset = TipoTrabajo.objects.all()
    serializer_class = TipoTrabajoSerializer
