from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import CampoCliente
from ..serializers import CampoClienteSerializer

class CampoClienteCreateAPIView(generics.CreateAPIView):
    queryset = CampoCliente.objects.all()
    serializer_class = CampoClienteSerializer

class CampoClienteUpdateAPIView(generics.UpdateAPIView):
    queryset = CampoCliente.objects.all()
    serializer_class = CampoClienteSerializer

class CampoClienteDestroyAPIView(generics.DestroyAPIView):
    queryset = CampoCliente.objects.all()
    serializer_class = CampoClienteSerializer

class CampoClienteDesactivarView(APIView):
    def patch(self, request, pk):
        cc = get_object_or_404(CampoCliente, pk=pk)
        cc.activo = False
        cc.save()
        serializer = CampoClienteSerializer(cc)
        return Response(serializer.data)
