from rest_framework import generics

from ..models import TareaRecordatorio
from ..serializers import TareaRecordatorioSerializer
from ..utils import get_usuario_id_from_request


class TareaRecordatorioCreateAPIView(generics.CreateAPIView):
    queryset = TareaRecordatorio.objects.all()
    serializer_class = TareaRecordatorioSerializer

    def perform_create(self, serializer):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save()


class TareaRecordatorioUpdateAPIView(generics.UpdateAPIView):
    serializer_class = TareaRecordatorioSerializer

    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return TareaRecordatorio.objects.filter(usuario_id=usuario_id)
        return TareaRecordatorio.objects.none()


class TareaRecordatorioDestroyAPIView(generics.DestroyAPIView):
    serializer_class = TareaRecordatorioSerializer

    def get_queryset(self):
        usuario_id = get_usuario_id_from_request(self.request)
        if usuario_id:
            return TareaRecordatorio.objects.filter(usuario_id=usuario_id)
        return TareaRecordatorio.objects.none()
