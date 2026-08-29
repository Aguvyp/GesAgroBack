from rest_framework import generics
from ..models import Usuario
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsSuperadmin
from ..serializers import AdminUsuarioSerializer


class SuperadminUsuarioMixin:
    queryset = Usuario.objects.all().order_by('email')
    serializer_class = AdminUsuarioSerializer
    permission_classes = [IsAuthenticated, IsSuperadmin]

class UsuarioCreateAPIView(SuperadminUsuarioMixin, generics.CreateAPIView):
    pass

class UsuarioUpdateAPIView(SuperadminUsuarioMixin, generics.UpdateAPIView):
    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

class UsuarioDestroyAPIView(SuperadminUsuarioMixin, generics.DestroyAPIView):
    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('No puede eliminar su propio usuario.')
        super().perform_destroy(instance)
