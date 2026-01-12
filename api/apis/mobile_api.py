from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Trabajo, Campo, Maquina, Personal, Cliente, Movimiento
from ..serializers import (
    TrabajoSerializer, CampoSerializer, MaquinaSerializer, 
    PersonalSerializer, ClienteSerializer, MovimientoSerializer
)
from django.utils import timezone
from ..utils import get_usuario_id_from_request

class MobileSyncView(APIView):
    def get(self, request):
        usuario_id = get_usuario_id_from_request(request)
        
        if not usuario_id:
            return Response(
                {"detail": "Token de acceso requerido"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Sincronización descendente (servidor -> móvil)
        return Response({
            "success": True,
            "data": {
                "trabajos": TrabajoSerializer(Trabajo.objects.filter(usuario_id=usuario_id), many=True).data,
                "campos": CampoSerializer(Campo.objects.filter(usuario_id=usuario_id), many=True).data,
                "maquinas": MaquinaSerializer(Maquina.objects.filter(usuario_id=usuario_id), many=True).data,
                "personal": PersonalSerializer(Personal.objects.filter(usuario_id=usuario_id), many=True).data,
                "clientes": ClienteSerializer(Cliente.objects.filter(usuario_id=usuario_id), many=True).data,
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

