from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from ..models import Trabajo, Movimiento, Factura, Mantenimiento, Insumo, Campo, Maquina, Personal, Cliente
from django.utils import timezone
from ..utils import get_usuario_id_from_request

class DashboardResumenView(APIView):
    def get(self, request):
        usuario_id = get_usuario_id_from_request(request)
        
        if not usuario_id:
            return Response(
                {"detail": "Token de acceso requerido"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Trabajos
        trabajos_pendientes = Trabajo.objects.filter(usuario_id=usuario_id, estado='Pendiente').count()
        trabajos_en_curso = Trabajo.objects.filter(usuario_id=usuario_id, estado='En curso').count()
        trabajos_completados = Trabajo.objects.filter(usuario_id=usuario_id, estado='Completado').count()
        
        # Finanzas del mes
        movimientos_mes = Movimiento.objects.filter(usuario_id=usuario_id, fecha__gte=first_day_of_month)
        ingresos_mes = movimientos_mes.filter(es_cobro=True).aggregate(Sum('monto'))['monto__sum'] or 0.0
        gastos_mes = movimientos_mes.filter(es_cobro=False).aggregate(Sum('monto'))['monto__sum'] or 0.0
        
        # Facturas
        facturas_pendientes = Factura.objects.filter(usuario_id=usuario_id, estado='Pendiente').count()
        facturas_vencidas = Factura.objects.filter(usuario_id=usuario_id, estado='Pendiente', fecha_vencimiento__lt=now.date()).count()
        
        # Otros
        mantenimientos_pendientes = Mantenimiento.objects.filter(usuario_id=usuario_id, estado='Pendiente').count()
        
        # Para evitar errores si Insumo no tiene stock_minimo (aunque lo definí)
        try:
            from django.db.models import F
            insumos_bajo_stock = Insumo.objects.filter(usuario_id=usuario_id, stock_actual__lte=F('stock_minimo')).count()
        except:
            insumos_bajo_stock = 0

        return Response({
            "trabajos_pendientes": trabajos_pendientes,
            "trabajos_en_curso": trabajos_en_curso,
            "trabajos_completados": trabajos_completados,
            "ingresos_mes": ingresos_mes,
            "gastos_mes": gastos_mes,
            "balance_mes": ingresos_mes - gastos_mes,
            "facturas_pendientes": facturas_pendientes,
            "facturas_vencidas": facturas_vencidas,
            "mantenimientos_pendientes": mantenimientos_pendientes,
            "insumos_bajo_stock": insumos_bajo_stock
        })

class DashboardEstadisticasView(APIView):
    def get(self, request):
        usuario_id = get_usuario_id_from_request(request)
        
        if not usuario_id:
            return Response(
                {"detail": "Token de acceso requerido"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response({
            "total_trabajos": Trabajo.objects.filter(usuario_id=usuario_id).count(),
            "total_campos": Campo.objects.filter(usuario_id=usuario_id).count(),
            "total_maquinas": Maquina.objects.filter(usuario_id=usuario_id).count(),
            "total_personal": Personal.objects.filter(usuario_id=usuario_id).count(),
            "total_clientes": Cliente.objects.filter(usuario_id=usuario_id).count(),
            "superficie_total_ha": Campo.objects.filter(usuario_id=usuario_id).aggregate(Sum('hectareas'))['hectareas__sum'] or 0.0,
            "ingresos_totales": Movimiento.objects.filter(usuario_id=usuario_id, es_cobro=True).aggregate(Sum('monto'))['monto__sum'] or 0.0,
            "gastos_totales": Movimiento.objects.filter(usuario_id=usuario_id, es_cobro=False).aggregate(Sum('monto'))['monto__sum'] or 0.0,
            "balance_total": (Movimiento.objects.filter(usuario_id=usuario_id, es_cobro=True).aggregate(Sum('monto'))['monto__sum'] or 0.0) - 
                             (Movimiento.objects.filter(usuario_id=usuario_id, es_cobro=False).aggregate(Sum('monto'))['monto__sum'] or 0.0)
        })

class FlutterDashboardResumenView(DashboardResumenView):
    def get(self, request):
        res = super().get(request)
        return Response({
            "success": True,
            "data": res.data
        })

