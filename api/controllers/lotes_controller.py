from rest_framework import generics
from rest_framework.exceptions import ValidationError
from ..models import Lote, Cliente
from ..serializers import LoteSerializer
from ..utils import get_usuario_id_from_request


class _LoteOwnershipMixin:
    serializer_class = LoteSerializer

    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return Lote.objects.filter(usuario_id=usuario_id).select_related('campo')
        return Lote.objects.none()

    def _validate_lote_data(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        validated_data = serializer.validated_data
        campo = validated_data.get('campo') or getattr(serializer.instance, 'campo', None)
        cliente_id = validated_data.get('cliente_id', getattr(serializer.instance, 'cliente_id', None))

        if not usuario_id:
            raise ValidationError('Token de acceso requerido')

        if campo is None:
            raise ValidationError('Debe especificar un campo para el lote')

        if campo.usuario_id != usuario_id:
            raise ValidationError('El campo indicado no existe o no pertenece al usuario')

        if cliente_id:
            if not Cliente.objects.filter(id=cliente_id, usuario_id=usuario_id).exists():
                raise ValidationError('El cliente indicado no existe o no pertenece al usuario')

        return usuario_id


class LoteCreateAPIView(_LoteOwnershipMixin, generics.CreateAPIView):
    queryset = Lote.objects.all()

    def perform_create(self, serializer):
        usuario_id = self._validate_lote_data(serializer)
        campo = serializer.validated_data.get('campo')
        cliente_id = serializer.validated_data.get('cliente_id')

        if usuario_id:
            serializer.save(
                usuario_id=usuario_id,
                cliente_id=cliente_id or getattr(campo, 'cliente_id', None),
            )
        else:
            serializer.save()


class LoteUpdateAPIView(_LoteOwnershipMixin, generics.UpdateAPIView):
    def perform_update(self, serializer):
        usuario_id = self._validate_lote_data(serializer)
        campo = serializer.validated_data.get('campo')
        cliente_id = serializer.validated_data.get('cliente_id')

        save_kwargs = {'usuario_id': usuario_id}
        if 'cliente_id' in serializer.validated_data or 'campo' in serializer.validated_data:
            save_kwargs['cliente_id'] = cliente_id or getattr(campo, 'cliente_id', None)

        serializer.save(**save_kwargs)


class LoteDestroyAPIView(_LoteOwnershipMixin, generics.DestroyAPIView):
    pass
