from rest_framework import serializers
from .models import (
    Usuario, Personal, Campo, Cliente, Maquina, CampoCliente, 
    Costo, Factura, FacturaItem, Credito, CuotaCredito, Pago, 
    Movimiento, Mantenimiento, Insumo, TipoTrabajo, Trabajo, 
    TrabajoPersonal, AuthToken
)

# --- Auth Serializers ---

class UsuarioSerializer(serializers.ModelSerializer):
    ultimo_acceso = serializers.DateTimeField(source='last_login', read_only=True, allow_null=True)
    activo = serializers.BooleanField(source='is_active', read_only=False)
    
    class Meta:
        model = Usuario
        fields = ('id', 'nombre', 'email', 'rol', 'activo', 'fecha_creacion', 'ultimo_acceso')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    dni = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    nombre = serializers.CharField(required=False, allow_blank=True)
    rol = serializers.CharField(required=False, default='Operario')
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
            'rol': validated_data.get('rol', 'Operario'),
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

# --- Entidades Serializers ---

class CampoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campo
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
    superficie_total_ha = serializers.FloatField(default=0.0, read_only=True)
    horas_trabajadas = serializers.FloatField(default=0.0, read_only=True)
    trabajos_completados = serializers.IntegerField(default=0, read_only=True)
    ultimo_trabajo = serializers.CharField(default='', read_only=True)

    class Meta:
        model = Personal
        fields = '__all__'

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
    
    id_personal = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    id_maquinas = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    personal_hectareas = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

    personal_detail = TrabajoPersonalSerializer(source='trabajopersonal_set', many=True, read_only=True)

    class Meta:
        model = Trabajo
        fields = '__all__'
        extra_kwargs = {
            'personal': {'read_only': True},
            'maquinas': {'read_only': True},
        }

    def create(self, validated_data):
        id_personal = validated_data.pop('id_personal', [])
        id_maquinas = validated_data.pop('id_maquinas', [])
        personal_hectareas = validated_data.pop('personal_hectareas', [])
        
        trabajo = Trabajo.objects.create(**validated_data)
        
        if id_maquinas:
            trabajo.maquinas.set(id_maquinas)
            
        if personal_hectareas:
            for item in personal_hectareas:
                TrabajoPersonal.objects.create(
                    trabajo=trabajo,
                    personal_id=item['id'],
                    hectareas=item.get('ha', 0)
                )
        elif id_personal:
            for p_id in id_personal:
                TrabajoPersonal.objects.create(trabajo=trabajo, personal_id=p_id)
                
        return trabajo

    def update(self, instance, validated_data):
        id_personal = validated_data.pop('id_personal', None)
        id_maquinas = validated_data.pop('id_maquinas', None)
        personal_hectareas = validated_data.pop('personal_hectareas', None)
        
        instance = super().update(instance, validated_data)
        
        if id_maquinas is not None:
            instance.maquinas.set(id_maquinas)
            
        if personal_hectareas is not None:
            TrabajoPersonal.objects.filter(trabajo=instance).delete()
            for item in personal_hectareas:
                TrabajoPersonal.objects.create(
                    trabajo=instance,
                    personal_id=item['id'],
                    hectareas=item.get('ha', 0)
                )
        elif id_personal is not None:
            TrabajoPersonal.objects.filter(trabajo=instance).delete()
            for p_id in id_personal:
                TrabajoPersonal.objects.create(trabajo=instance, personal_id=p_id)
                
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

