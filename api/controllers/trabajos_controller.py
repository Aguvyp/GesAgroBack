from rest_framework import generics, status
from rest_framework.response import Response
from ..models import Trabajo
from ..serializers import TrabajoSerializer, RegistrarHorasSerializer
from ..utils import get_usuario_id_from_request

class TrabajoCreateAPIView(generics.CreateAPIView):
    queryset = Trabajo.objects.all()
    serializer_class = TrabajoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class TrabajoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = TrabajoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Trabajo.objects.filter(usuario_id=usuario_id)
        return Trabajo.objects.none()

class TrabajoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = TrabajoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Trabajo.objects.filter(usuario_id=usuario_id)
        return Trabajo.objects.none()

from django.db.models import Sum

class RegistrarHorasView(generics.CreateAPIView):
    # No necesitamos queryset específico porque es solo Create
    serializer_class = RegistrarHorasSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validación de hectáreas (Regla manual requerida: devolver 200 con error)
        trabajo = serializer.validated_data.get('trabajo')
        hectareas = serializer.validated_data.get('hectareas')
        
        if trabajo and trabajo.campo and hectareas:
            limit_hectareas = float(trabajo.campo.hectareas or 0)
            if limit_hectareas > 0:
                current_total = trabajo.trabajopersonal_set.aggregate(total=Sum('hectareas'))['total'] or 0.0
                total_maybe = float(current_total) + float(hectareas)
                
                if total_maybe > limit_hectareas:
                    return Response(
                        {"detail": "Se excede de horas del total declarado para el campo en el que trabaja"},
                        status=status.HTTP_200_OK
                    )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()