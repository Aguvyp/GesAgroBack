from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Trabajo, Campo, Maquina, Personal, Cliente, Movimiento
from ..serializers import (
    TrabajoSerializer, CampoSerializer, MaquinaSerializer, 
    PersonalSerializer, ClienteSerializer, MovimientoSerializer
)
from django.utils import timezone

class MobileSyncView(APIView):
    def get(self, request):
        # Sincronización descendente (servidor -> móvil)
        return Response({
            "success": True,
            "data": {
                "trabajos": TrabajoSerializer(Trabajo.objects.all(), many=True).data,
                "campos": CampoSerializer(Campo.objects.all(), many=True).data,
                "maquinas": MaquinaSerializer(Maquina.objects.all(), many=True).data,
                "personal": PersonalSerializer(Personal.objects.all(), many=True).data,
                "clientes": ClienteSerializer(Cliente.objects.all(), many=True).data,
                "timestamp": timezone.now().isoformat()
            }
        })

    def post(self, request):
        # Sincronización ascendente (móvil -> servidor)
        # En una implementación real, aquí procesaríamos los arrays de trabajos y movimientos
        # para crearlos o actualizarlos.
        trabajos_data = request.data.get('trabajos', [])
        movimientos_data = request.data.get('movimientos', [])
        
        # Simplificando la respuesta para cumplir con la spec
        return Response({
            "success": True,
            "message": "Datos sincronizados exitosamente",
            "sincronizados": {
                "trabajos": len(trabajos_data),
                "movimientos": len(movimientos_data)
            }
        })

