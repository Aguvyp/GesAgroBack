from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    AuthToken,
    Campo,
    Personal,
    TipoTrabajo,
    Trabajo,
    TrabajoPersonal,
    Usuario,
)


class MobileApiContractTest(APITestCase):
    """Contrato mínimo que la aplicación Flutter necesita para operar."""

    @classmethod
    def setUpTestData(cls):
        cls.user = Usuario.objects.create_user(
            email='mobile@example.com',
            password='ClaveSegura123',
            nombre='Usuario Mobile',
        )

    def login(self):
        response = self.client.post(
            reverse('auth-login'),
            {'email': self.user.email, 'password': 'ClaveSegura123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access_token'])
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access_token']}"
        )
        return response.data

    def test_protected_collections_require_bearer_token(self):
        response = self.client.get(reverse('campo-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_and_core_collections_match_mobile_contract(self):
        login = self.login()
        self.assertEqual(login['usuario_id'], self.user.id)

        for route_name in (
            'campo-list',
            'lote-list',
            'cliente-list',
            'maquina-list',
            'personal-list',
            'trabajo-list',
            'costo-list',
            'factura-list',
            'credito-list',
            'cuota-credito-list',
            'pago-list',
            'movimiento-list',
            'mantenimiento-list',
            'insumo-list',
            'tipo-trabajo-list',
        ):
            response = self.client.get(reverse(route_name))
            self.assertEqual(response.status_code, status.HTTP_200_OK, route_name)
            self.assertIsInstance(response.data, list, route_name)

    def test_trabajo_personal_detail_is_available_to_mobile(self):
        self.login()
        campo = Campo.objects.create(
            nombre='Campo contrato',
            hectareas=100,
            usuario_id=self.user.id,
        )
        tipo = TipoTrabajo.objects.create(trabajo='Siembra contrato')
        personal = Personal.objects.create(
            nombre='Operario contrato',
            dni='CONTRATO-1',
            usuario_id=self.user.id,
        )
        trabajo = Trabajo.objects.create(
            id_tipo_trabajo=tipo,
            cultivo='Soja',
            fecha_inicio=date.today(),
            campo=campo,
            usuario_id=self.user.id,
        )
        registro = TrabajoPersonal.objects.create(
            trabajo=trabajo,
            personal=personal,
            hectareas=10,
            horas_trabajadas=2,
            usuario_id=self.user.id,
        )

        response = self.client.get(
            reverse('trabajo-personal-detail', kwargs={'pk': registro.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], registro.id)

    def test_mobile_relationship_payloads_are_persisted(self):
        self.login()

        cliente = self.client.post(
            reverse('cliente-create'),
            {'nombre': 'Cliente contrato'},
            format='json',
        )
        self.assertEqual(cliente.status_code, status.HTTP_201_CREATED)

        campo = self.client.post(
            reverse('campo-create'),
            {'nombre': 'Campo contrato', 'hectareas': 80},
            format='json',
        )
        self.assertEqual(campo.status_code, status.HTTP_201_CREATED)

        maquina = self.client.post(
            reverse('maquina-create'),
            {'nombre': 'Máquina contrato'},
            format='json',
        )
        self.assertEqual(maquina.status_code, status.HTTP_201_CREATED)

        credito = self.client.post(
            reverse('credito-create'),
            {'entidad': 'Banco contrato', 'monto_otorgado': 1000},
            format='json',
        )
        self.assertEqual(credito.status_code, status.HTTP_201_CREATED)

        mantenimiento = self.client.post(
            reverse('mantenimiento-create'),
            {
                'maquina': maquina.data['id'],
                'fecha': date.today().isoformat(),
                'descripcion': 'Service',
            },
            format='json',
        )
        self.assertEqual(mantenimiento.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mantenimiento.data['maquina'], maquina.data['id'])

        factura = self.client.post(
            reverse('factura-create'),
            {
                'cliente': cliente.data['id'],
                'numero': 'CONTRATO-1',
                'fecha_emision': date.today().isoformat(),
                'fecha_vencimiento': date.today().isoformat(),
                'monto_total': 500,
            },
            format='json',
        )
        self.assertEqual(factura.status_code, status.HTTP_201_CREATED)
        self.assertEqual(factura.data['cliente'], cliente.data['id'])

        cuota = self.client.post(
            reverse('cuota-credito-create'),
            {
                'credito': credito.data['id'],
                'numero_cuota': 1,
                'fecha_vencimiento': date.today().isoformat(),
                'monto_total': 100,
            },
            format='json',
        )
        self.assertEqual(cuota.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cuota.data['credito'], credito.data['id'])

        tipo = TipoTrabajo.objects.create(trabajo='Cosecha contrato')
        trabajo = self.client.post(
            reverse('trabajo-create'),
            {
                'id_tipo_trabajo': tipo.id,
                'campo': campo.data['id'],
                'cultivo': 'Trigo',
                'fecha_inicio': date.today().isoformat(),
            },
            format='json',
        )
        self.assertEqual(trabajo.status_code, status.HTTP_201_CREATED)
        self.assertEqual(trabajo.data['campo'], campo.data['id'])

    def test_logout_invalidates_the_mobile_token(self):
        login = self.login()
        response = self.client.post(reverse('auth-logout'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            AuthToken.objects.get(access_token=login['access_token']).is_active
        )

        response = self.client.get(reverse('campo-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
