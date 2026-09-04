from django.urls import path
from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .controllers.auth_controller import RegisterView, LoginView, UpdatePasswordView, TestView, SessionView, HealthCheckView, LogoutView
from .apis.tareas_recordatorio_api import get_tareas_recordatorio
from .controllers.tareas_recordatorio_controller import (
    TareaRecordatorioCreateAPIView,
    TareaRecordatorioDestroyAPIView,
    TareaRecordatorioUpdateAPIView,
)
from .apis.usuarios_api import get_usuarios
from .controllers.usuarios_controller import UsuarioCreateAPIView, UsuarioUpdateAPIView, UsuarioDestroyAPIView
from .apis.campos_api import get_campos
from .controllers.campos_controller import CampoCreateAPIView, CampoUpdateAPIView, CampoDestroyAPIView
from .apis.lotes_api import get_lotes
from .controllers.lotes_controller import LoteCreateAPIView, LoteUpdateAPIView, LoteDestroyAPIView
from .apis.clientes_api import get_clientes
from .controllers.clientes_controller import ClienteCreateAPIView, ClienteUpdateAPIView, ClienteDestroyAPIView
from .apis.maquinas_api import get_maquinas
from .controllers.maquinas_controller import MaquinaCreateAPIView, MaquinaUpdateAPIView, MaquinaDestroyAPIView
from .apis.personal_api import get_personal, validate_dni
from .controllers.personal_controller import PersonalCreateAPIView, PersonalUpdateAPIView, PersonalDestroyAPIView
from .apis.trabajos_api import (
    get_trabajos, get_trabajo_detalle,
    marcar_indicaciones_enviadas,
    update_trabajo_personal, delete_trabajo_personal
)
from .controllers.trabajos_controller import (
    TrabajoCreateAPIView, TrabajoUpdateAPIView, 
    TrabajoDestroyAPIView, RegistrarHorasView
)
from .controllers.trabajo_personal_controller import TrabajoPersonalDetailView


from .apis.tipo_trabajo_api import get_tipo_trabajo
from .controllers.tipo_trabajo_controller import TipoTrabajoCreateAPIView, TipoTrabajoUpdateAPIView, TipoTrabajoDestroyAPIView
from .apis.costos_api import get_costos, get_costos_pagados, get_costos_pendientes
from .controllers.costos_controller import CostoCreateAPIView, CostoUpdateAPIView, CostoDestroyAPIView
from .apis.facturas_api import get_facturas
from .controllers.facturas_controller import FacturaCreateAPIView, FacturaUpdateAPIView, FacturaDestroyAPIView
from .apis.creditos_api import get_creditos
from .controllers.creditos_controller import CreditoCreateAPIView, CreditoUpdateAPIView, CreditoDestroyAPIView
from .apis.cuotas_credito_api import get_cuotas_credito
from .controllers.cuotas_credito_controller import CuotaCreditoCreateAPIView, CuotaCreditoUpdateAPIView, CuotaCreditoDestroyAPIView
from .apis.pagos_api import get_pagos
from .controllers.pagos_controller import PagoCreateAPIView, PagoUpdateAPIView, PagoDestroyAPIView
from .apis.movimientos_api import get_movimientos
from .controllers.movimientos_controller import MovimientoCreateAPIView, MovimientoUpdateAPIView, MovimientoDestroyAPIView
from .apis.mantenimientos_api import get_mantenimientos
from .controllers.mantenimientos_controller import MantenimientoCreateAPIView, MantenimientoUpdateAPIView, MantenimientoDestroyAPIView
from .apis.insumos_api import get_insumos
from .controllers.insumos_controller import InsumoCreateAPIView, InsumoUpdateAPIView, InsumoDestroyAPIView
from .apis.campos_cliente_api import get_campos_cliente
from .controllers.campos_cliente_controller import (
    CampoClienteCreateAPIView, CampoClienteUpdateAPIView,
    CampoClienteDestroyAPIView, CampoClienteDesactivarView
)
from .apis.flutter_api import (
    FlutterTrabajoListView, FlutterCampoListView, FlutterMaquinaListView,
    FlutterPersonalListView, FlutterClienteListView, FlutterCostoListView,
    FlutterFacturaListView
)
from .apis.dashboard_api import (
    DashboardResumenView, DashboardEstadisticasView, FlutterDashboardResumenView
)
from .apis.reportes_api import ReporteTrabajosView, ReporteFinancieroView
from .apis.mobile_api import MobileSyncView
from .apis.telegram_api import telegram_webhook
from .apis.weather_api import get_weather_forecast, weather_health
from .controllers.marketplace_controller import (
    MiPerfilMarketplaceView, ServiciosMarketplaceView,
    ServicioMarketplaceDetailView, PedidosMarketplaceView,
    PedidoMarketplaceDetailView, MapaMarketplaceView, ContactoMarketplaceView,
)

urlpatterns = [
    # Marketplace geolocalizado
    path('marketplace/perfil/', MiPerfilMarketplaceView.as_view(), name='marketplace-profile'),
    path('marketplace/mapa/', MapaMarketplaceView.as_view(), name='marketplace-map'),
    path('marketplace/servicios/', ServiciosMarketplaceView.as_view(), name='marketplace-services'),
    path('marketplace/servicios/<int:pk>/', ServicioMarketplaceDetailView.as_view(), name='marketplace-service-detail'),
    path('marketplace/pedidos/', PedidosMarketplaceView.as_view(), name='marketplace-orders'),
    path('marketplace/pedidos/<int:pk>/', PedidoMarketplaceDetailView.as_view(), name='marketplace-order-detail'),
    path('marketplace/contacto/<str:tipo>/<int:pk>/', ContactoMarketplaceView.as_view(), name='marketplace-contact'),

    # Clima
    path('clima/pronostico/', get_weather_forecast, name='weather-forecast'),
    path('clima/pronostico', get_weather_forecast),
    path('clima/test/', weather_health, name='weather-test'),

    # Swagger
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Auth & Health
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/update-password/', UpdatePasswordView.as_view(), name='auth-update-password'),
    path('auth/test/', TestView.as_view(), name='auth-test'),
    path('auth/session/', SessionView.as_view(), name='auth-session'),
    path('health/', HealthCheckView.as_view(), name='health'),

    # Tareas recordatorio
    path('tareas-recordatorio/', get_tareas_recordatorio, name='tarea-recordatorio-list'),
    path('tareas-recordatorio/<int:pk>/', get_tareas_recordatorio, name='tarea-recordatorio-detail'),
    path('tareas-recordatorio/create/', TareaRecordatorioCreateAPIView.as_view(), name='tarea-recordatorio-create'),
    path('tareas-recordatorio/<int:pk>/update/', TareaRecordatorioUpdateAPIView.as_view(), name='tarea-recordatorio-update'),
    path('tareas-recordatorio/<int:pk>/delete/', TareaRecordatorioDestroyAPIView.as_view(), name='tarea-recordatorio-delete'),

    # Usuarios
    path('usuarios/', get_usuarios, name='usuario-list'),
    path('usuarios/<int:pk>/', get_usuarios, name='usuario-detail'),
    path('usuarios/create/', UsuarioCreateAPIView.as_view(), name='usuario-create'),
    path('usuarios/<int:pk>/update/', UsuarioUpdateAPIView.as_view(), name='usuario-update'),
    path('usuarios/<int:pk>/delete/', UsuarioDestroyAPIView.as_view(), name='usuario-delete'),

    # Campos
    path('campos/', get_campos, name='campo-list'),
    path('campos/<int:pk>/', get_campos, name='campo-detail'),
    path('campos/create/', CampoCreateAPIView.as_view(), name='campo-create'),
    path('campos/<int:pk>/update/', CampoUpdateAPIView.as_view(), name='campo-update'),
    path('campos/<int:pk>/delete/', CampoDestroyAPIView.as_view(), name='campo-delete'),

    # Lotes
    path('lotes/', get_lotes, name='lote-list'),
    path('lotes/<int:pk>/', get_lotes, name='lote-detail'),
    path('lotes/create/', LoteCreateAPIView.as_view(), name='lote-create'),
    path('lotes/<int:pk>/update/', LoteUpdateAPIView.as_view(), name='lote-update'),
    path('lotes/<int:pk>/delete/', LoteDestroyAPIView.as_view(), name='lote-delete'),

    # Clientes
    path('clientes/', get_clientes, name='cliente-list'),
    path('clientes/<int:pk>/', get_clientes, name='cliente-detail'),
    path('clientes/create/', ClienteCreateAPIView.as_view(), name='cliente-create'),
    path('clientes/<int:pk>/update/', ClienteUpdateAPIView.as_view(), name='cliente-update'),
    path('clientes/<int:pk>/delete/', ClienteDestroyAPIView.as_view(), name='cliente-delete'),

    # Campos-Cliente
    path('campos-cliente/', get_campos_cliente, name='campos-cliente-list'),
    path('campos-cliente/<int:pk>/', get_campos_cliente, name='campos-cliente-detail'),
    path('campos-cliente/create/', CampoClienteCreateAPIView.as_view(), name='campos-cliente-create'),
    path('campos-cliente/<int:pk>/update/', CampoClienteUpdateAPIView.as_view(), name='campos-cliente-update'),
    path('campos-cliente/<int:pk>/delete/', CampoClienteDestroyAPIView.as_view(), name='campos-cliente-delete'),
    path('campos-cliente/<int:pk>/desactivar/', CampoClienteDesactivarView.as_view(), name='campos-cliente-desactivar'),

    # Máquinas
    path('maquinas/', get_maquinas, name='maquina-list'),
    path('maquinas/<int:pk>/', get_maquinas, name='maquina-detail'),
    path('maquinas/create/', MaquinaCreateAPIView.as_view(), name='maquina-create'),
    path('maquinas/<int:pk>/update/', MaquinaUpdateAPIView.as_view(), name='maquina-update'),
    path('maquinas/<int:pk>/delete/', MaquinaDestroyAPIView.as_view(), name='maquina-delete'),

    # Personal
    path('personal/create/', PersonalCreateAPIView.as_view(), name='personal-create'),
    path('personal/validate-dni/', validate_dni, name='personal-validate-dni'),
    path('personal/', get_personal, name='personal-list'),
    path('personal/<int:pk>/', get_personal, name='personal-detail'),
    path('personal/<int:pk>/update/', PersonalUpdateAPIView.as_view(), name='personal-update'),
    path('personal/<int:pk>/delete/', PersonalDestroyAPIView.as_view(), name='personal-delete'),

    # Trabajos
    path('trabajos/create/', TrabajoCreateAPIView.as_view(), name='trabajo-create'),
    path('trabajos/registrar-horas/', RegistrarHorasView.as_view(), name='trabajo-registrar-horas'),
    path('trabajos/detalle/<int:pk>/', get_trabajo_detalle, name='trabajo-full-detail'),
    path('trabajos/', get_trabajos, name='trabajo-list'),
    path('trabajos/<int:pk>/', get_trabajos, name='trabajo-detail'),
    path('trabajos/<int:pk>/indicaciones/enviadas/', marcar_indicaciones_enviadas, name='trabajo-indicaciones-enviadas'),
    path('trabajos/<int:pk>/update/', TrabajoUpdateAPIView.as_view(), name='trabajo-update'),
    path('trabajos/<int:pk>/delete/', TrabajoDestroyAPIView.as_view(), name='trabajo-delete'),

    # Trabajo Personal (Horas individuales)
    path('trabajos-personal/<int:pk>/', TrabajoPersonalDetailView.as_view(), name='trabajo-personal-detail'),
    path('trabajos-personal/create/', RegistrarHorasView.as_view(), name='trabajo-personal-create'),
    path('trabajos-personal/<int:pk>/update/', update_trabajo_personal, name='trabajo-personal-update'),
    path('trabajos-personal/<int:pk>/delete/', delete_trabajo_personal, name='trabajo-personal-delete'),

    # Tipo Trabajo
    path('tipo-trabajo/', get_tipo_trabajo, name='tipo-trabajo-list'),
    path('tipo-trabajo/<int:pk>/', get_tipo_trabajo, name='tipo-trabajo-detail'),
    path('tipo-trabajo/create/', TipoTrabajoCreateAPIView.as_view(), name='tipo-trabajo-create'),
    path('tipo-trabajo/<int:pk>/update/', TipoTrabajoUpdateAPIView.as_view(), name='tipo-trabajo-update'),
    path('tipo-trabajo/<int:pk>/delete/', TipoTrabajoDestroyAPIView.as_view(), name='tipo-trabajo-delete'),

    # Costos
    path('costos/create/', CostoCreateAPIView.as_view(), name='costo-create'),
    path('costos/pagados/', get_costos_pagados, name='costos-pagados'),
    path('costos/pendientes/', get_costos_pendientes, name='costos-pendientes'),
    path('costos/', get_costos, name='costo-list'),
    path('costos/<int:pk>/', get_costos, name='costo-detail'),
    path('costos/<int:pk>/update/', CostoUpdateAPIView.as_view(), name='costo-update'),
    path('costos/<int:pk>/delete/', CostoDestroyAPIView.as_view(), name='costo-delete'),

    # Facturas
    path('facturas/', get_facturas, name='factura-list'),
    path('facturas/<int:pk>/', get_facturas, name='factura-detail'),
    path('facturas/create/', FacturaCreateAPIView.as_view(), name='factura-create'),
    path('facturas/<int:pk>/update/', FacturaUpdateAPIView.as_view(), name='factura-update'),
    path('facturas/<int:pk>/delete/', FacturaDestroyAPIView.as_view(), name='factura-delete'),

    # Créditos
    path('creditos/', get_creditos, name='credito-list'),
    path('creditos/<int:pk>/', get_creditos, name='credito-detail'),
    path('creditos/create/', CreditoCreateAPIView.as_view(), name='credito-create'),
    path('creditos/<int:pk>/update/', CreditoUpdateAPIView.as_view(), name='credito-update'),
    path('creditos/<int:pk>/delete/', CreditoDestroyAPIView.as_view(), name='credito-delete'),

    # Cuotas Crédito
    path('cuotas-credito/', get_cuotas_credito, name='cuota-credito-list'),
    path('cuotas-credito/<int:pk>/', get_cuotas_credito, name='cuota-credito-detail'),
    path('cuotas-credito/create/', CuotaCreditoCreateAPIView.as_view(), name='cuota-credito-create'),
    path('cuotas-credito/<int:pk>/update/', CuotaCreditoUpdateAPIView.as_view(), name='cuota-credito-update'),
    path('cuotas-credito/<int:pk>/delete/', CuotaCreditoDestroyAPIView.as_view(), name='cuota-credito-delete'),

    # Pagos
    path('pagos/', get_pagos, name='pago-list'),
    path('pagos/<int:pk>/', get_pagos, name='pago-detail'),
    path('pagos/create/', PagoCreateAPIView.as_view(), name='pago-create'),
    path('pagos/<int:pk>/update/', PagoUpdateAPIView.as_view(), name='pago-update'),
    path('pagos/<int:pk>/delete/', PagoDestroyAPIView.as_view(), name='pago-delete'),

    # Movimientos
    path('movimientos/', get_movimientos, name='movimiento-list'),
    path('movimientos/<int:pk>/', get_movimientos, name='movimiento-detail'),
    path('movimientos/create/', MovimientoCreateAPIView.as_view(), name='movimiento-create'),
    path('movimientos/<int:pk>/update/', MovimientoUpdateAPIView.as_view(), name='movimiento-update'),
    path('movimientos/<int:pk>/delete/', MovimientoDestroyAPIView.as_view(), name='movimiento-delete'),

    # Mantenimientos
    path('mantenimientos/', get_mantenimientos, name='mantenimiento-list'),
    path('mantenimientos/<int:pk>/', get_mantenimientos, name='mantenimiento-detail'),
    path('mantenimientos/create/', MantenimientoCreateAPIView.as_view(), name='mantenimiento-create'),
    path('mantenimientos/<int:pk>/update/', MantenimientoUpdateAPIView.as_view(), name='mantenimiento-update'),
    path('mantenimientos/<int:pk>/delete/', MantenimientoDestroyAPIView.as_view(), name='mantenimiento-delete'),

    # Insumos
    path('insumos/', get_insumos, name='insumo-list'),
    path('insumos/<int:pk>/', get_insumos, name='insumo-detail'),
    path('insumos/create/', InsumoCreateAPIView.as_view(), name='insumo-create'),
    path('insumos/<int:pk>/update/', InsumoUpdateAPIView.as_view(), name='insumo-update'),
    path('insumos/<int:pk>/delete/', InsumoDestroyAPIView.as_view(), name='insumo-delete'),

    # Endpoints Optimizados Flutter
    path('flutter/trabajos/lista/', FlutterTrabajoListView.as_view(), name='flutter-trabajo-list'),
    path('flutter/campos/lista/', FlutterCampoListView.as_view(), name='flutter-campo-list'),
    path('flutter/maquinas/lista/', FlutterMaquinaListView.as_view(), name='flutter-maquina-list'),
    path('flutter/personal/lista/', FlutterPersonalListView.as_view(), name='flutter-personal-list'),
    path('flutter/clientes/lista/', FlutterClienteListView.as_view(), name='flutter-cliente-list'),
    path('flutter/costos/lista/', FlutterCostoListView.as_view(), name='flutter-costo-list'),
    path('flutter/facturas/lista/', FlutterFacturaListView.as_view(), name='flutter-factura-list'),
    path('flutter/dashboard/resumen/', FlutterDashboardResumenView.as_view(), name='flutter-dashboard-resumen'),

    # Dashboard y Reportes
    path('dashboard/resumen/', DashboardResumenView.as_view(), name='dashboard-resumen'),
    path('dashboard/estadisticas/', DashboardEstadisticasView.as_view(), name='dashboard-estadisticas'),
    path('reportes/trabajos/', ReporteTrabajosView.as_view(), name='reporte-trabajos'),
    path('reportes/financiero/', ReporteFinancieroView.as_view(), name='reporte-financiero'),

    # Endpoints Móviles
    path('mobile/sync/', MobileSyncView.as_view(), name='mobile-sync'),


    # Telegram Webhook
    path('telegram/webhook/', telegram_webhook, name='telegram-webhook'),
]
