from rest_framework import serializers
from .models import (
    Usuario, Personal, Campo, Lote, Cliente, Maquina, CampoCliente, 
    Costo, Factura, FacturaItem, Credito, CuotaCredito, Pago, 
    Movimiento, Mantenimiento, Insumo, TipoTrabajo, Trabajo, 
    TrabajoPersonal, AuthToken, TareaRecordatorio, PerfilMarketplace,
    ServicioMarketplace, PedidoServicioMarketplace
)

# --- Auth Serializers ---

class UsuarioSerializer(serializers.ModelSerializer):
    ultimo_acceso = serializers.DateTimeField(source='last_login', read_only=True, allow_null=True)
    activo = serializers.BooleanField(source='is_active', read_only=False)
    
    class Meta:
        model = Usuario
        fields = ('id', 'nombre', 'email', 'rol', 'activo', 'fecha_creacion', 'ultimo_acceso')

class AdminUsuarioSerializer(UsuarioSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    rol = serializers.ChoiceField(choices=('Dueño', 'Empleado'))

    class Meta(UsuarioSerializer.Meta):
        fields = UsuarioSerializer.Meta.fields + ('password',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        activo = validated_data.pop('is_active', True)
        return Usuario.objects.create_user(
            password=password,
            is_active=activo,
            **validated_data,
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save(update_fields=['password'])
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    dni = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    nombre = serializers.CharField(required=False, allow_blank=True)
    rol = serializers.CharField(required=False, default='Empleado')
    is_staff = serializers.BooleanField(required=False, default=False)
    is_superuser = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Usuario
        fields = ('nombre', 'email', 'password', 'dni', 'telefono', 'rol', 'is_staff', 'is_superuser')

    def create(self, validated_data):
        dni = validated_data.pop('dni', None)
        
        # Preparar campos extra para el usuario
        extra_fields = {
            'nombre': validated_data.get('nombre', ''),
            'telefono': validated_data.get('telefono', ''),
            'rol': validated_data.get('rol', 'Empleado'),
            'is_staff': validated_data.get('is_staff', False),
            'is_superuser': validated_data.get('is_superuser', False),
        }
        
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            **extra_fields
        )
        
        Personal.objects.create(
            nombre=user.nombre,
            dni=dni,
            telefono=user.telefono,
            usuario_id=user.id
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UpdatePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class AuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthToken
        fields = ['id', 'access_token', 'usuario_id', 'created_at', 'expires_at', 'is_active']
        read_only_fields = ['id', 'access_token', 'created_at']

class TareaRecordatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaRecordatorio
        fields = '__all__'
        read_only_fields = ('id', 'usuario_id', 'created_at', 'updated_at')


class PerfilMarketplaceSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='usuario.email', read_only=True)

    class Meta:
        model = PerfilMarketplace
        fields = (
            'id', 'tipo', 'nombre_publico', 'descripcion', 'telefono_contacto',
            'email', 'localidad', 'latitud', 'longitud', 'radio_cobertura_km',
            'activo', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'email', 'created_at', 'updated_at')


class MarketplacePublicMixin:
    def validate_latitud(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError('Latitud fuera de rango.')
        return value

    def validate_longitud(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError('Longitud fuera de rango.')
        return value

    def get_nombre_publico(self, obj):
        try:
            return obj.usuario.perfil_marketplace.nombre_publico
        except PerfilMarketplace.DoesNotExist:
            return obj.usuario.nombre or 'Usuario GesAgro'

    def get_es_propio(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.id == obj.usuario_id)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Aproximadamente 100 m: suficiente para descubrir oferta/demanda sin
        # revelar una ubicación privada exacta.
        data['latitud'] = round(float(instance.latitud), 3)
        data['longitud'] = round(float(instance.longitud), 3)
        return data


class ServicioMarketplaceSerializer(MarketplacePublicMixin, serializers.ModelSerializer):
    propietario_id = serializers.IntegerField(source='usuario_id', read_only=True)
    nombre_publico = serializers.SerializerMethodField()
    es_propio = serializers.SerializerMethodField()

    class Meta:
        model = ServicioMarketplace
        fields = (
            'id', 'propietario_id', 'nombre_publico', 'es_propio', 'titulo',
            'categoria', 'descripcion', 'latitud', 'longitud',
            'radio_cobertura_km', 'disponible', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'propietario_id', 'nombre_publico', 'es_propio', 'created_at', 'updated_at')


class PedidoServicioMarketplaceSerializer(MarketplacePublicMixin, serializers.ModelSerializer):
    propietario_id = serializers.IntegerField(source='usuario_id', read_only=True)
    nombre_publico = serializers.SerializerMethodField()
    es_propio = serializers.SerializerMethodField()

    class Meta:
        model = PedidoServicioMarketplace
        fields = (
            'id', 'propietario_id', 'nombre_publico', 'es_propio', 'titulo',
            'categoria', 'descripcion', 'latitud', 'longitud', 'hectareas',
            'fecha_necesaria', 'estado', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'propietario_id', 'nombre_publico', 'es_propio', 'created_at', 'updated_at')

# --- Entidades Serializers ---

class CampoSerializer(serializers.ModelSerializer):
    lotes_count = serializers.SerializerMethodField()

    def get_lotes_count(self, obj):
        return obj.lotes.count()

    class Meta:
        model = Campo
        fields = '__all__'

class LoteSerializer(serializers.ModelSerializer):
    campo_nombre = serializers.ReadOnlyField(source='campo.nombre')
    campo_latitud = serializers.ReadOnlyField(source='campo.latitud')
    campo_longitud = serializers.ReadOnlyField(source='campo.longitud')

    class Meta:
        model = Lote
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class MaquinaSerializer(serializers.ModelSerializer):
    superficie_total_ha = serializers.FloatField(default=0.0, read_only=True)
    horas_trabajadas = serializers.FloatField(default=0.0, read_only=True)
    ultimo_trabajo = serializers.CharField(default='', read_only=True)
    
    class Meta:
        model = Maquina
        fields = '__all__'

class PersonalSerializer(serializers.ModelSerializer):
    dni = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    superficie_total_ha = serializers.FloatField(default=0.0, read_only=True)
    horas_trabajadas = serializers.FloatField(default=0.0, read_only=True)
    trabajos_completados = serializers.IntegerField(default=0, read_only=True)
    ultimo_trabajo = serializers.CharField(default='', read_only=True)

    class Meta:
        model = Personal
        fields = '__all__'

    def validate_dni(self, value):
        # Guardar los DNI vacíos como NULL permite registrar varias personas
        # sin DNI sin violar la restricción unique de la base de datos.
        if value is None or not value.strip():
            return None
        return value.strip()

class CampoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoCliente
        fields = '__all__'

# --- Trabajo Serializers ---

class TipoTrabajoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTrabajo
        fields = '__all__'

class TrabajoPersonalSerializer(serializers.ModelSerializer):
    nombre = serializers.ReadOnlyField(source='personal.nombre')
    dni = serializers.ReadOnlyField(source='personal.dni')
    # rol obtenido de otra manera ya que no hay relación directa usuario en Personal
    rol = serializers.SerializerMethodField()
    
    id_personal = serializers.ReadOnlyField(source='personal.id')
    id_trabajo_personal = serializers.ReadOnlyField(source='id')

    def get_rol(self, obj):
        # Intentar obtener el rol buscando el usuario por nombre
        try:
            usuario = Usuario.objects.get(nombre=obj.personal.nombre)
            return usuario.rol
        except Usuario.DoesNotExist:
            return None

    class Meta:
        model = TrabajoPersonal
        fields = ('id', 'id_trabajo_personal', 'id_personal', 'nombre', 'dni', 'rol', 'hectareas', 'horas_trabajadas', 'fecha', 'hora_inicio', 'hora_fin')

class RegistrarHorasSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrabajoPersonal
        fields = ('trabajo', 'personal', 'hectareas', 'horas_trabajadas', 'fecha', 'hora_inicio', 'hora_fin')

    def validate(self, data):
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        
        # Calcular horas automáticamente si se pasan inicio y fin
        if hora_inicio and hora_fin:
            from datetime import datetime
            # Crear datetimes arbitrarios para restar
            dummy_date = datetime(2000, 1, 1)
            dt_inicio = datetime.combine(dummy_date, hora_inicio)
            dt_fin = datetime.combine(dummy_date, hora_fin)
            
            # Si el fin es menor que el inicio, asumimos que cruzó la medianoche
            if dt_fin < dt_inicio:
                from datetime import timedelta
                dt_fin += timedelta(days=1)
                
            diff = dt_fin - dt_inicio
            horas = diff.total_seconds() / 3600
            data['horas_trabajadas'] = round(horas, 2)
        elif 'horas_trabajadas' not in data:
            # Si no se calculan y no se pasan, default a 0
            data['horas_trabajadas'] = 0
            
        return data


class TrabajoSerializer(serializers.ModelSerializer):
    tipo = serializers.ReadOnlyField(source='id_tipo_trabajo.trabajo')
    campo_nombre = serializers.ReadOnlyField(source='campo.nombre')
    campo_ha = serializers.ReadOnlyField(source='campo.hectareas')
    lote_nombre = serializers.ReadOnlyField(source='lote.nombre')
    lote_ha = serializers.ReadOnlyField(source='lote.hectareas')
    lote_polygon_geojson = serializers.ReadOnlyField(source='lote.polygon_geojson')
    lote_punto_acceso_latitud = serializers.ReadOnlyField(source='lote.punto_acceso_latitud')
    lote_punto_acceso_longitud = serializers.ReadOnlyField(source='lote.punto_acceso_longitud')
    lote_punto_entrada_latitud = serializers.ReadOnlyField(source='lote.punto_entrada_latitud')
    lote_punto_entrada_longitud = serializers.ReadOnlyField(source='lote.punto_entrada_longitud')
    lote_notas_acceso = serializers.ReadOnlyField(source='lote.notas_acceso')
    
    id_personal = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
        allow_null=True,
        default=list
    )
    id_maquinas = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
        allow_null=True,
        default=list
    )
    personal_hectareas = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True,
        allow_null=True,
        default=list
    )

    personal_detail = TrabajoPersonalSerializer(source='trabajopersonal_set', many=True, read_only=True)

    class Meta:
        model = Trabajo
        fields = '__all__'
        extra_kwargs = {
            'personal': {'read_only': True},
            'maquinas': {'read_only': True},
        }

    def validate(self, data):
        campo = data.get('campo') or getattr(self.instance, 'campo', None)
        lote = data.get('lote') or getattr(self.instance, 'lote', None)

        if lote and campo and lote.campo_id != campo.id:
            raise serializers.ValidationError({
                'lote': 'El lote seleccionado no pertenece al campo indicado.'
            })

        return data

    def create(self, validated_data):
        id_personal = validated_data.pop('id_personal', None) or []
        id_maquinas = validated_data.pop('id_maquinas', None) or []
        personal_hectareas = validated_data.pop('personal_hectareas', None) or []
        usuario_id = validated_data.get('usuario_id')
        
        trabajo = Trabajo.objects.create(**validated_data)
        
        if id_maquinas:
            trabajo.maquinas.set(id_maquinas)
            
        if personal_hectareas:
            for item in personal_hectareas:
                TrabajoPersonal.objects.create(
                    trabajo=trabajo,
                    personal_id=item['id'],
                    hectareas=item.get('ha', 0),
                    usuario_id=usuario_id
                )
        elif id_personal:
            for p_id in id_personal:
                TrabajoPersonal.objects.create(
                    trabajo=trabajo,
                    personal_id=p_id,
                    usuario_id=usuario_id,
                )
                
        return trabajo

    def update(self, instance, validated_data):
        id_personal = validated_data.pop('id_personal', None)
        id_maquinas = validated_data.pop('id_maquinas', None)
        personal_hectareas = validated_data.pop('personal_hectareas', None)
        usuario_id = validated_data.get('usuario_id', instance.usuario_id)
        
        instance = super().update(instance, validated_data)
        
        if id_maquinas is not None:
            instance.maquinas.set(id_maquinas)
            
        if personal_hectareas is not None:
            TrabajoPersonal.objects.filter(trabajo=instance).delete()
            for item in personal_hectareas:
                TrabajoPersonal.objects.create(
                    trabajo=instance,
                    personal_id=item['id'],
                    hectareas=item.get('ha', 0),
                    usuario_id=usuario_id,
                )
        elif id_personal is not None:
            TrabajoPersonal.objects.filter(trabajo=instance).delete()
            for p_id in id_personal:
                TrabajoPersonal.objects.create(
                    trabajo=instance,
                    personal_id=p_id,
                    usuario_id=usuario_id,
                )
                
        return instance

# --- Finanzas Serializers ---

class CostoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Costo
        fields = '__all__'

class FacturaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaItem
        fields = '__all__'
        extra_kwargs = {'factura': {'required': False}}

class FacturaSerializer(serializers.ModelSerializer):
    items = FacturaItemSerializer(many=True, required=False)

    class Meta:
        model = Factura
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        factura = Factura.objects.create(**validated_data)
        for item_data in items_data:
            FacturaItem.objects.create(factura=factura, **item_data)
        return factura

class CreditoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credito
        fields = '__all__'

class CuotaCreditoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaCredito
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = '__all__'

# --- Otros Serializers ---

class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantenimiento
        fields = '__all__'

class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = '__all__'

