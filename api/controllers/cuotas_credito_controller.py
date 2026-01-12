from rest_framework import generics
from ..models import CuotaCredito, Credito
from ..serializers import CuotaCreditoSerializer
from ..utils import get_usuario_id_from_request

class CuotaCreditoCreateAPIView(generics.CreateAPIView):
    queryset = CuotaCredito.objects.all()
    serializer_class = CuotaCreditoSerializer
    
    def perform_create(self, serializer):
        # No asignamos usuario_id directamente porque CuotaCredito no tiene usuario_id
        # pero validamos que el crédito padre pertenezca al usuario
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id and 'credito' in serializer.validated_data:
            credito = serializer.validated_data['credito']
            if credito.usuario_id != usuario_id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("No tienes permiso para crear cuotas de este crédito")
        serializer.save()

class CuotaCreditoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CuotaCreditoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            creditos_usuario = Credito.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
            return CuotaCredito.objects.filter(credito_id__in=creditos_usuario)
        return CuotaCredito.objects.none()

class CuotaCreditoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CuotaCreditoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            creditos_usuario = Credito.objects.filter(usuario_id=usuario_id).values_list('id', flat=True)
            return CuotaCredito.objects.filter(credito_id__in=creditos_usuario)
        return CuotaCredito.objects.none()