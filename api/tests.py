from datetime import date
from unittest.mock import patch
import uuid

from django.test import TestCase
from rest_framework.test import APIClient

from .models import (
    Usuario, Personal, Campo, Cliente, Maquina, CampoCliente,
    TipoTrabajo, Trabajo, TrabajoPersonal, Costo, Factura, FacturaItem,
    Credito, CuotaCredito, Pago, Movimiento, Mantenimiento, Insumo
)
from .services.auth_token_service import create_auth_token


class GesAgroEndpointTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'SuperSecret123!'
        cls.user = Usuario.objects.create_user(
            email='test-coverage@example.com',
            password=cls.password,
            nombre='Tester Cobertura',
            telefono='+5491112345678'
        )
        cls.token = create_auth_token(cls.user.id)

        cls.tipo_trabajo = TipoTrabajo.objects.create(trabajo='Siembra')
        cls.campo = Campo.objects.create(
            nombre='Campo Maestro',
            hectareas=55.5,
            usuario_id=cls.user.id
        )
        cls.cliente = Cliente.objects.create(
            nombre='Cliente Maestro',
            telefono='+5491123456789',
            usuario_id=cls.user.id
        )
        cls.campo_cliente = CampoCliente.objects.create(
            cliente=cls.cliente,
            campo=cls.campo,
            usuario_id=cls.user.id
        )
        cls.maquina = Maquina.objects.create(
            nombre='Tractor Test',
            usuario_id=cls.user.id
        )
        cls.personal = Personal.objects.create(
            nombre='Operario Test',
            dni='98765432',
            telefono='+5491199999999',
            usuario_id=cls.user.id
        )
        cls.trabajo = Trabajo.objects.create(
            id_tipo_trabajo=cls.tipo_trabajo,
            campo=cls.campo,
            fecha_inicio=date.today(),
            estado='Pendiente',
            usuario_id=cls.user.id
        )
        cls.trabajo_personal = TrabajoPersonal.objects.create(
            trabajo=cls.trabajo,
            personal=cls.personal,
            hectareas=8,
            horas_trabajadas=2,
            fecha=date.today(),
            usuario_id=cls.user.id
        )
        cls.costo_pendiente = Costo.objects.create(
            monto=150,
            fecha=date.today(),
            destinatario='Proveedor Demo',
            pagado=False,
            categoria='Gastos',
            usuario_id=cls.user.id
        )
        cls.costo_pagado = Costo.objects.create(
            monto=120,
            fecha=date.today(),
            destinatario='Proveedor Demo 2',
            pagado=True,
            categoria='Servicios',
            usuario_id=cls.user.id
        )
        cls.factura = Factura.objects.create(
            cliente=cls.cliente,
            numero='F-0000',
            fecha_emision=date.today(),
            fecha_vencimiento=date.today(),
            monto_total=400,
            estado='Pendiente',
            usuario_id=cls.user.id
        )
        FacturaItem.objects.create(
            factura=cls.factura,
            descripcion='Servicio test',
            cantidad=1,
            precio_unitario=400,
            subtotal=400
        )
        cls.credito = Credito.objects.create(
            entidad='Banco Demo',
            monto_otorgado=5000,
            usuario_id=cls.user.id
        )
        cls.cuota = CuotaCredito.objects.create(
            credito=cls.credito,
            numero_cuota=1,
            fecha_vencimiento=date.today(),
            monto_total=2500,
            usuario_id=cls.user.id
        )
        cls.pago = Pago.objects.create(
            monto=200,
            fecha=date.today(),
            metodo_pago='Transferencia',
            id_factura=cls.factura,
            usuario_id=cls.user.id
        )
        cls.movimiento_ingreso = Movimiento.objects.create(
            monto=220,
            fecha=date.today(),
            categoria='Venta',
            es_cobro=True,
            pagado=True,
            usuario_id=cls.user.id
        )
        cls.movimiento_gasto = Movimiento.objects.create(
            monto=110,
            fecha=date.today(),
            categoria='Compra',
            es_cobro=False,
            pagado=False,
            usuario_id=cls.user.id
        )
        cls.mantenimiento = Mantenimiento.objects.create(
            maquina=cls.maquina,
            fecha=date.today(),
            estado='Pendiente',
            usuario_id=cls.user.id
        )
        cls.insumo = Insumo.objects.create(
            nombre='Fertilizante Test',
            categoria='Fertilizantes',
            usuario_id=cls.user.id
        )

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def _url(self, path: str) -> str:
        path = path.lstrip('/')
        return f'/api/{path}'

    @staticmethod
    def _unique_email() -> str:
        return f"test-{uuid.uuid4().hex[:6]}@example.com"

    def test_auth_endpoints(self):
        register_payload = {
            'nombre': 'Registrado',
            'email': self._unique_email(),
            'password': 'OtraContra1234!',
            'rol': 'Contable'
        }
        register_resp = self.client.post(self._url('auth/register/'), register_payload, format='json')
        self.assertEqual(register_resp.status_code, 201)

        login_payload = {
            'email': self.user.email,
            'password': self.password
        }
        login_resp = self.client.post(self._url('auth/login/'), login_payload, format='json')
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn('access_token', login_resp.data)

        update_payload = {
            'email': self.user.email,
            'password': 'NewPass123!'
        }
        update_resp = self.client.post(self._url('auth/update-password/'), update_payload, format='json')
        self.assertEqual(update_resp.status_code, 200)

    def test_logout_takes_token_offline(self):
        temp_token = create_auth_token(self.user.id)
        temp_client = APIClient()
        temp_client.credentials(HTTP_AUTHORIZATION=f'Bearer {temp_token.access_token}')
        logout_resp = temp_client.post(self._url('auth/logout/'), format='json')
        self.assertEqual(logout_resp.status_code, 200)

        down_resp = temp_client.get(self._url('campos/'))
        self.assertEqual(down_resp.status_code, 401)

    def test_read_endpoints(self):
        cases = [
            ('auth/test/', {}),
            ('health/', {}),
            ('schema/', {}),
            ('schema/swagger-ui/', {}),
            ('clima/test/', {}),
            ('usuarios/', {}),
            (f'usuarios/{self.user.id}/', {}),
            ('campos/', {}),
            (f'campos/{self.campo.id}/', {}),
            ('clientes/', {}),
            (f'clientes/{self.cliente.id}/', {}),
            ('campos-cliente/', {}),
            (f'campos-cliente/{self.campo_cliente.id}/', {}),
            ('maquinas/', {}),
            (f'maquinas/{self.maquina.id}/', {}),
            ('personal/', {}),
            (f'personal/{self.personal.id}/', {}),
            ('personal/validate-dni/', {'params': {'dni': self.personal.dni}}),
            ('trabajos/', {}),
            (f'trabajos/{self.trabajo.id}/', {}),
            (f'trabajos/detalle/{self.trabajo.id}/', {}),
            ('tipo-trabajo/', {}),
            (f'tipo-trabajo/{self.tipo_trabajo.id}/', {}),
            ('costos/', {}),
            (f'costos/{self.costo_pendiente.id}/', {}),
            ('costos/pagados/', {}),
            ('costos/pendientes/', {}),
            ('facturas/', {}),
            (f'facturas/{self.factura.id}/', {}),
            ('creditos/', {}),
            (f'creditos/{self.credito.id}/', {}),
            ('cuotas-credito/', {}),
            (f'cuotas-credito/{self.cuota.id}/', {}),
            ('pagos/', {}),
            (f'pagos/{self.pago.id}/', {}),
            ('movimientos/', {}),
            (f'movimientos/{self.movimiento_ingreso.id}/', {}),
            ('mantenimientos/', {}),
            (f'mantenimientos/{self.mantenimiento.id}/', {}),
            ('insumos/', {}),
            (f'insumos/{self.insumo.id}/', {}),
            ('flutter/trabajos/lista/', {'params': {'estado': 'Pendiente'}}),
            ('flutter/campos/lista/', {}),
            ('flutter/maquinas/lista/', {}),
            ('flutter/personal/lista/', {}),
            ('flutter/clientes/lista/', {}),
            ('flutter/costos/lista/', {}),
            ('flutter/facturas/lista/', {}),
            ('flutter/dashboard/resumen/', {}),
            ('dashboard/resumen/', {}),
            ('dashboard/estadisticas/', {}),
            ('reportes/trabajos/', {}),
            ('reportes/financiero/', {}),
            ('mobile/sync/', {})
        ]

        for path, kwargs in cases:
            response = self.client.get(self._url(path), **kwargs)
            self.assertLess(response.status_code, 400, msg=path)

    def test_create_endpoints(self):
        today = date.today().isoformat()
        create_cases = [
            ('campos/create/', {'nombre': 'Campo Prueba', 'hectareas': 10}),
            ('clientes/create/', {'nombre': 'Cliente Prueba'}),
            ('campos-cliente/create/', {'campo': self.campo.id, 'cliente': self.cliente.id}),
            ('maquinas/create/', {'nombre': 'Maquina Prueba'}),
            ('personal/create/', {'nombre': 'Personal Nuevo', 'dni': '11223344', 'telefono': '+5491177777777'}),
            ('tipo-trabajo/create/', {'trabajo': 'Laboreo'}),
            ('costos/create/', {'monto': 45, 'fecha': today, 'destinatario': 'Cosecha'}),
            ('facturas/create/', {
                'numero': f'F-{uuid.uuid4().hex[:6]}',
                'fecha_emision': today,
                'fecha_vencimiento': today,
                'monto_total': 120,
                'estado': 'Pendiente',
                'cliente': self.cliente.id
            }),
            ('creditos/create/', {'entidad': 'Coope', 'monto_otorgado': 1000}),
            ('cuotas-credito/create/', {
                'credito': self.credito.id,
                'numero_cuota': 2,
                'fecha_vencimiento': today,
                'monto_total': 500
            }),
            ('pagos/create/', {'monto': 30, 'fecha': today, 'metodo_pago': 'Efectivo', 'id_factura': self.factura.id}),
            ('movimientos/create/', {'monto': 60, 'fecha': today, 'categoria': 'Combustible', 'es_cobro': False}),
            ('mantenimientos/create/', {'maquina': self.maquina.id, 'fecha': today}),
            ('insumos/create/', {'nombre': 'Semilla Extra'}),
            ('trabajos/create/', {
                'id_tipo_trabajo': self.tipo_trabajo.id,
                'campo': self.campo.id,
                'fecha_inicio': today
            }),
            ('trabajos/registrar-horas/', {
                'trabajo': self.trabajo.id,
                'personal': self.personal.id,
                'fecha': today,
                'hora_inicio': '08:00:00',
                'hora_fin': '10:00:00'
            }),
            ('trabajos-personal/create/', {
                'trabajo': self.trabajo.id,
                'personal': self.personal.id,
                'fecha': today,
                'hectareas': 2,
                'horas_trabajadas': 2
            })
        ]

        for path, payload in create_cases:
            response = self.client.post(self._url(path), payload, format='json')
            self.assertLess(response.status_code, 400, msg=path)

    def test_update_endpoints(self):
        update_cases = [
            (f'usuarios/{self.user.id}/update/', {'nombre': 'Usuario Actualizado'}),
            (f'campos/{self.campo.id}/update/', {'detalles': 'Actualizado'}),
            (f'clientes/{self.cliente.id}/update/', {'direccion': 'Nueva Dirección'}),
            (f'campos-cliente/{self.campo_cliente.id}/update/', {'observaciones': 'Notas actualizadas'}),
            (f'maquinas/{self.maquina.id}/update/', {'estado': 'En mantenimiento'}),
            (f'personal/{self.personal.id}/update/', {'telefono': '+5491188888888'}),
            (f'trabajos/{self.trabajo.id}/update/', {'estado': 'En curso'}),
            (f'tipo-trabajo/{self.tipo_trabajo.id}/update/', {'trabajo': 'Laboreo suave'}),
            (f'costos/{self.costo_pendiente.id}/update/', {'pagado': True}),
            (f'facturas/{self.factura.id}/update/', {'estado': 'Completado'}),
            (f'creditos/{self.credito.id}/update/', {'estado': 'Cancelado'}),
            (f'cuotas-credito/{self.cuota.id}/update/', {'estado': 'Pagada'}),
            (f'pagos/{self.pago.id}/update/', {'descripcion': 'Pago actualizado'}),
            (f'movimientos/{self.movimiento_ingreso.id}/update/', {'categoria': 'Ventas especiales'}),
            (f'mantenimientos/{self.mantenimiento.id}/update/', {'estado': 'Completado'}),
            (f'insumos/{self.insumo.id}/update/', {'stock_actual': 999}),
            (f'trabajos-personal/{self.trabajo_personal.id}/update/', {'hectareas': 9})
        ]

        for path, payload in update_cases:
            response = self.client.patch(self._url(path), payload, format='json')
            self.assertLess(response.status_code, 400, msg=path)

        desactivar_resp = self.client.patch(self._url(f'campos-cliente/{self.campo_cliente.id}/desactivar/'))
        self.assertEqual(desactivar_resp.status_code, 200)
        self.assertFalse(desactivar_resp.data.get('activo', True))

    def test_delete_endpoints(self):
        def make_user():
            return Usuario.objects.create_user(email=self._unique_email(), password='Temp1234!', nombre='TempDelete')

        def make_campo():
            return Campo.objects.create(nombre='Temp Campo', usuario_id=self.user.id)

        def make_cliente():
            return Cliente.objects.create(nombre='Temp Cliente', usuario_id=self.user.id)

        def make_campo_cliente():
            campo = Campo.objects.create(nombre='Temp Campo CC', usuario_id=self.user.id)
            cliente = Cliente.objects.create(nombre='Temp Cliente CC', usuario_id=self.user.id)
            return CampoCliente.objects.create(cliente=cliente, campo=campo, usuario_id=self.user.id)

        def make_maquina():
            return Maquina.objects.create(nombre='Temp Maq', usuario_id=self.user.id)

        def make_personal():
            return Personal.objects.create(nombre='Temp Operario', dni=str(uuid.uuid4())[:8], usuario_id=self.user.id)

        def make_trabajo():
            return Trabajo.objects.create(
                id_tipo_trabajo=self.tipo_trabajo,
                campo=self.campo,
                fecha_inicio=date.today(),
                usuario_id=self.user.id
            )

        def make_tipo_trabajo():
            return TipoTrabajo.objects.create(trabajo='Temp Tipo')

        def make_costo():
            return Costo.objects.create(monto=10, fecha=date.today(), destinatario='Temp', usuario_id=self.user.id)

        def make_factura():
            cliente = Cliente.objects.create(nombre='Temp Cliente F', usuario_id=self.user.id)
            factura = Factura.objects.create(
                cliente=cliente,
                numero=f'F1-{uuid.uuid4().hex[:4]}',
                fecha_emision=date.today(),
                fecha_vencimiento=date.today(),
                monto_total=50,
                usuario_id=self.user.id
            )
            Pago.objects.create(monto=10, fecha=date.today(), metodo_pago='Efectivo', id_factura=factura, usuario_id=self.user.id)
            return factura

        def make_credito():
            return Credito.objects.create(entidad='Temp Banco', monto_otorgado=1000, usuario_id=self.user.id)

        def make_cuota():
            credito = make_credito()
            return CuotaCredito.objects.create(credito=credito, numero_cuota=3, fecha_vencimiento=date.today(), monto_total=100, usuario_id=self.user.id)

        def make_pago():
            factura = make_factura()
            return Pago.objects.create(monto=20, fecha=date.today(), metodo_pago='QB', id_factura=factura, usuario_id=self.user.id)

        def make_movimiento():
            return Movimiento.objects.create(monto=30, fecha=date.today(), categoria='Temp', es_cobro=True, usuario_id=self.user.id)

        def make_mantenimiento():
            maquina = make_maquina()
            return Mantenimiento.objects.create(maquina=maquina, fecha=date.today(), usuario_id=self.user.id)

        def make_insumo():
            return Insumo.objects.create(nombre='Temp Insumo', usuario_id=self.user.id)

        delete_actions = [
            ('usuarios/{id}/delete/', make_user),
            ('campos/{id}/delete/', make_campo),
            ('clientes/{id}/delete/', make_cliente),
            ('campos-cliente/{id}/delete/', make_campo_cliente),
            ('maquinas/{id}/delete/', make_maquina),
            ('personal/{id}/delete/', make_personal),
            ('trabajos/{id}/delete/', make_trabajo),
            ('tipo-trabajo/{id}/delete/', make_tipo_trabajo),
            ('costos/{id}/delete/', make_costo),
            ('facturas/{id}/delete/', make_factura),
            ('creditos/{id}/delete/', make_credito),
            ('cuotas-credito/{id}/delete/', make_cuota),
            ('pagos/{id}/delete/', make_pago),
            ('movimientos/{id}/delete/', make_movimiento),
            ('mantenimientos/{id}/delete/', make_mantenimiento),
            ('insumos/{id}/delete/', make_insumo)
        ]

        for template, factory in delete_actions:
            instance = factory()
            response = self.client.delete(self._url(template.format(id=instance.id)))
            self.assertEqual(response.status_code, 204, msg=template)

        temp_trabajo = make_trabajo()
        temp_personal = make_personal()
        temp_trabajo_personal = TrabajoPersonal.objects.create(
            trabajo=temp_trabajo,
            personal=temp_personal,
            fecha=date.today(),
            usuario_id=self.user.id
        )
        resp = self.client.delete(self._url(f'trabajos-personal/{temp_trabajo_personal.id}/delete/'))
        self.assertEqual(resp.status_code, 204)

    @patch('api.apis.weather_api.requests.get')
    def test_weather_endpoints(self, mock_get):
        payload = {
            'current': {
                'temperature_2m': 25,
                'relative_humidity_2m': 60,
                'wind_speed_10m': 12,
                'weather_code': 0
            },
            'daily': {
                'time': ['2026-03-15', '2026-03-16'],
                'temperature_2m_max': [25, 26],
                'temperature_2m_min': [18, 19],
                'weather_code': [1, 2],
                'wind_speed_10m_max': [10, 11],
                'precipitation_probability_max': [5, 10]
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = payload

        params = {'lat': '-34', 'lon': '-58'}
        resp1 = self.client.get(self._url('clima/pronostico/'), params=params)
        resp2 = self.client.get(self._url('clima/pronostico'), params=params)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('actual', resp1.data)

    def test_mobile_sync_post(self):
        resp = self.client.post(
            self._url('mobile/sync/'),
            {'trabajos': [], 'movimientos': []},
            format='json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get('sincronizados', {}).get('trabajos'), 0)

    @patch('api.controllers.whatsapp_controller.process_with_openai')
    def test_whatsapp_webhook(self, mock_openai):
        mock_openai.return_value = (True, 'respuesta simulada')
        payload = {
            'From': 'whatsapp:+5491112345678',
            'Body': 'Hola',
            'NumMedia': '0'
        }
        response = self.client.post(self._url('whatsapp/webhook/'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('success'))
