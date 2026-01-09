from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Trabajo, Campo, Maquina, Personal, Cliente, Costo, Factura
from ..serializers import (
    TrabajoSerializer, CampoSerializer, MaquinaSerializer, 
    PersonalSerializer, ClienteSerializer, CostoSerializer, 
    FacturaSerializer
)

class FlutterBaseListView(APIView):
    model = None
    serializer_class = None

    def get(self, request):
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 100))
        
        queryset = self.model.objects.all()
        
        # Filtrado opcional (ejemplo para trabajos)
        if self.model == Trabajo and request.query_params.get('estado'):
            queryset = queryset.filter(estado=request.query_params.get('estado'))
            
        total = queryset.count()
        data = queryset[skip:skip+limit]
        serializer = self.serializer_class(data, many=True)
        
        return Response({
            "success": True,
            "data": serializer.data,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total
            }
        })

class FlutterTrabajoListView(FlutterBaseListView):
    model = Trabajo
    serializer_class = TrabajoSerializer

class FlutterCampoListView(FlutterBaseListView):
    model = Campo
    serializer_class = CampoSerializer

class FlutterMaquinaListView(FlutterBaseListView):
    model = Maquina
    serializer_class = MaquinaSerializer

class FlutterPersonalListView(FlutterBaseListView):
    model = Personal
    serializer_class = PersonalSerializer

class FlutterClienteListView(FlutterBaseListView):
    model = Cliente
    serializer_class = ClienteSerializer

class FlutterCostoListView(FlutterBaseListView):
    model = Costo
    serializer_class = CostoSerializer

class FlutterFacturaListView(FlutterBaseListView):
    model = Factura
    serializer_class = FacturaSerializer

