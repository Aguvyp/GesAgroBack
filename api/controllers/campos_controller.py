from rest_framework import generics
from rest_framework.exceptions import ValidationError
from ..models import Campo, Cliente
from ..serializers import CampoSerializer
from ..utils import get_usuario_id_from_request

class CampoCreateAPIView(generics.CreateAPIView):
    queryset = Campo.objects.all()
    serializer_class = CampoSerializer
    
    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        validated_data = serializer.validated_data
        
        # Validar cliente_id si propio=False
        propio = validated_data.get('propio', True)
        cliente_id = validated_data.get('cliente_id')
        
        if not propio:
            if not cliente_id:
                raise ValidationError("Si el campo no es propio, debe especificar un cliente_id")
            
            # Validar que el cliente pertenezca al usuario
            if usuario_id:
                try:
                    cliente = Cliente.objects.get(id=cliente_id, usuario_id=usuario_id)
                except Cliente.DoesNotExist:
                    raise ValidationError(f"El cliente con ID {cliente_id} no existe o no pertenece al usuario")
        else:
            # Si es propio, asegurar que cliente_id sea None
            validated_data['cliente_id'] = None
        
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()

class CampoUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CampoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Campo.objects.filter(usuario_id=usuario_id)
        return Campo.objects.none()

class CampoDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CampoSerializer
    
    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Campo.objects.filter(usuario_id=usuario_id)
        return Campo.objects.none()