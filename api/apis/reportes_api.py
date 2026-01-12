from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from ..models import Trabajo, Movimiento, Factura
from django.utils import timezone
from ..utils import get_usuario_id_from_request

class ReporteTrabajosView(APIView):
    def get(self, request):
        usuario_id = get_usuario_id_from_request(request)
        
        if not usuario_id:
            return Response(
                {"detail": "Token de acceso requerido"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        now = timezone.now()
        periodo = request.query_params.get('periodo', now.strftime('%Y-%m'))
        
        trabajos = Trabajo.objects.filter(usuario_id=usuario_id, fecha_inicio__startswith=periodo)
        
        total_trabajos = trabajos.count()
        # Esto es un poco simplificado, en un entorno real usaríamos GroupBy
        por_tipo = {}
        for t in trabajos:
            tipo_nombre = t.id_tipo_trabajo.trabajo
            por_tipo[tipo_nombre] = por_tipo.get(tipo_nombre, 0) + 1
            
        por_estado = {
            "Pendiente": trabajos.filter(estado='Pendiente').count(),
            "En curso": trabajos.filter(estado='En curso').count(),
            "Completado": trabajos.filter(estado='Completado').count(),
        }
        
        # Superficie total de los campos de esos trabajos
        # Nota: Esto puede duplicar si hay varios trabajos en el mismo campo
        superficie = sum([t.campo.hectareas for t in trabajos])
        
        return Response({
            "periodo": periodo,
            "total_trabajos": total_trabajos,
            "trabajos_por_tipo": por_tipo,
            "trabajos_por_estado": por_estado,
            "superficie_total_ha": superficie,
            "ingresos_totales": trabajos.aggregate(Sum('monto_cobrado'))['monto_cobrado__sum'] or 0.0
        })

class ReporteFinancieroView(APIView):
    def get(self, request):
        usuario_id = get_usuario_id_from_request(request)
        
        if not usuario_id:
            return Response(
                {"detail": "Token de acceso requerido"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        now = timezone.now()
        periodo = request.query_params.get('periodo', now.strftime('%Y-%m'))
        
        movimientos = Movimiento.objects.filter(usuario_id=usuario_id, fecha__startswith=periodo)
        
        ingresos_total = movimientos.filter(es_cobro=True).aggregate(Sum('monto'))['monto__sum'] or 0.0
        gastos_total = movimientos.filter(es_cobro=False).aggregate(Sum('monto'))['monto__sum'] or 0.0
        
        # Categorías simplificadas
        gastos_por_cat = {}
        for m in movimientos.filter(es_cobro=False):
            gastos_por_cat[m.categoria] = gastos_por_cat.get(m.categoria, 0.0) + m.monto

        return Response({
            "periodo": periodo,
            "ingresos": {
                "total": ingresos_total,
                "por_categoria": {"Trabajos": ingresos_total} # Simplificado
            },
            "gastos": {
                "total": gastos_total,
                "por_categoria": gastos_por_cat
            },
            "balance": ingresos_total - gastos_total,
            "facturas_pendientes": Factura.objects.filter(usuario_id=usuario_id, estado='Pendiente').count(),
            "facturas_vencidas": Factura.objects.filter(usuario_id=usuario_id, estado='Pendiente', fecha_vencimiento__lt=now.date()).count()
        })

