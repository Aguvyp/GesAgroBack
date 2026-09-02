from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import PerfilMarketplace, ServicioMarketplace, PedidoServicioMarketplace
from ..serializers import (
    PerfilMarketplaceSerializer,
    ServicioMarketplaceSerializer,
    PedidoServicioMarketplaceSerializer,
)


class MiPerfilMarketplaceView(APIView):
    def get(self, request):
        perfil = PerfilMarketplace.objects.filter(usuario=request.user).first()
        if not perfil:
            return Response({'detail': 'Perfil no configurado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PerfilMarketplaceSerializer(perfil).data)

    def put(self, request):
        perfil = PerfilMarketplace.objects.filter(usuario=request.user).first()
        serializer = PerfilMarketplaceSerializer(perfil, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK if perfil else status.HTTP_201_CREATED)


class MarketplaceOwnedMixin:
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)


class ServiciosMarketplaceView(MarketplaceOwnedMixin, generics.ListCreateAPIView):
    queryset = ServicioMarketplace.objects.all()
    serializer_class = ServicioMarketplaceSerializer


class ServicioMarketplaceDetailView(MarketplaceOwnedMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = ServicioMarketplace.objects.all()
    serializer_class = ServicioMarketplaceSerializer


class PedidosMarketplaceView(MarketplaceOwnedMixin, generics.ListCreateAPIView):
    queryset = PedidoServicioMarketplace.objects.all()
    serializer_class = PedidoServicioMarketplaceSerializer


class PedidoMarketplaceDetailView(MarketplaceOwnedMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = PedidoServicioMarketplace.objects.all()
    serializer_class = PedidoServicioMarketplaceSerializer


class MapaMarketplaceView(APIView):
    def get(self, request):
        categoria = request.query_params.get('categoria', '').strip()
        servicios = ServicioMarketplace.objects.filter(disponible=True).select_related('usuario')
        pedidos = PedidoServicioMarketplace.objects.filter(estado='Publicado').select_related('usuario')
        if categoria:
            servicios = servicios.filter(Q(categoria__icontains=categoria) | Q(titulo__icontains=categoria))
            pedidos = pedidos.filter(Q(categoria__icontains=categoria) | Q(titulo__icontains=categoria))
        context = {'request': request}
        return Response({
            'servicios': ServicioMarketplaceSerializer(servicios, many=True, context=context).data,
            'pedidos': PedidoServicioMarketplaceSerializer(pedidos, many=True, context=context).data,
        })


class ContactoMarketplaceView(APIView):
    def get(self, request, tipo, pk):
        if tipo not in ('servicio', 'pedido'):
            return Response({'detail': 'Tipo de publicación inválido'}, status=status.HTTP_400_BAD_REQUEST)
        model = ServicioMarketplace if tipo == 'servicio' else PedidoServicioMarketplace
        publicacion = get_object_or_404(model.objects.select_related('usuario'), pk=pk)
        if publicacion.usuario_id == request.user.id:
            perfil = PerfilMarketplace.objects.filter(usuario=publicacion.usuario).first()
            return Response({
                'bloqueado': False,
                'telefono': perfil.telefono_contacto if perfil else '',
                'email': publicacion.usuario.email,
            })
        return Response({
            'bloqueado': True,
            'detail': 'El desbloqueo de contactos estará disponible próximamente.',
        })
