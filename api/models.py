from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # No usamos is_staff ni is_superuser porque no existen en la BD
        extra_fields.setdefault('rol', 'Administrador')
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser):
    ROLES = (
        ('Administrador', 'Administrador'),
        ('Contable', 'Contable'),
        ('Operario', 'Operario'),
    )
    nombre = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    # password viene de AbstractBaseUser
    rol = models.CharField(max_length=50, choices=ROLES, default='Operario', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    
    # Mapear is_active a activo (que existe en la BD)
    is_active = models.BooleanField(default=True, db_column='activo', null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Sobrescribir last_login de AbstractBaseUser y mapearlo a ultimo_acceso que existe en la BD
    last_login = models.DateTimeField(null=True, blank=True, db_column='ultimo_acceso')

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.email

class AuthToken(models.Model):
    access_token = models.CharField(max_length=255, unique=True, db_index=True)
    usuario_id = models.IntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_tokens'
        indexes = [
            models.Index(fields=['access_token']),
            models.Index(fields=['usuario_id']),
        ]
    
    def __str__(self):
        return f"Token for user {self.usuario_id}"

class TipoTrabajo(models.Model):
    trabajo = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tipo_trabajo'


    def __str__(self):
        return self.trabajo

class Campo(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    hectareas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    detalles = models.TextField(null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    propio = models.BooleanField(default=True, null=True, blank=True)
    cliente_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campos'

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.CharField(max_length=500, null=True, blank=True)
    cuit = models.CharField(max_length=20, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clientes'


    def __str__(self):
        return self.nombre

class CampoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='campos_asignados', null=True, blank=True)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='clientes_asignados', null=True, blank=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True, null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campos_cliente'
        unique_together = ('cliente', 'campo', 'activo')


class Maquina(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    marca = models.CharField(max_length=100, null=True, blank=True)
    modelo = models.CharField(max_length=100, null=True, blank=True)
    ano = models.IntegerField(null=True, blank=True)
    detalles = models.TextField(null=True, blank=True)
    ancho_trabajo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=50, default='Disponible', null=True, blank=True)
    superficie_total_ha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    ultimo_trabajo = models.CharField(max_length=255, null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'maquinas'


    def __str__(self):
        return self.nombre

class Personal(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    dni = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    superficie_total_ha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    trabajos_completados = models.IntegerField(default=0, null=True, blank=True)
    ultimo_trabajo = models.CharField(max_length=255, null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Campo usuario comentado porque la columna no existe en la base de datos
    # usuario = models.OneToOneField(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_info')

    class Meta:
        db_table = 'personal'


    def __str__(self):
        return self.nombre

class Trabajo(models.Model):
    id_tipo_trabajo = models.ForeignKey(TipoTrabajo, on_delete=models.PROTECT, related_name='trabajos', db_column='id_tipo_trabajo', null=True, blank=True)
    cultivo = models.CharField(max_length=255, null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='trabajos', null=True, blank=True)
    estado = models.CharField(max_length=50, default='Pendiente', null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    a_terceros = models.BooleanField(default=False, null=True, blank=True)
    cobrado = models.BooleanField(default=False, null=True, blank=True)
    monto_cobrado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cliente = models.CharField(max_length=255, null=True, blank=True)
    servicio_contratado = models.BooleanField(default=False, null=True, blank=True)
    rinde_cosecha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    humedad_cosecha = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    
    personal = models.ManyToManyField(Personal, through='TrabajoPersonal', related_name='trabajos')
    maquinas = models.ManyToManyField(Maquina, through='TrabajoMaquina', related_name='trabajos')

    class Meta:
        db_table = 'trabajos'


class TrabajoPersonal(models.Model):
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, null=True, blank=True)
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, null=True, blank=True)
    hectareas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trabajo_personal'
        unique_together = ('trabajo', 'personal')


class TrabajoMaquina(models.Model):
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, null=True, blank=True)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trabajo_maquinas'
        unique_together = ('trabajo', 'maquina')


class Costo(models.Model):
    monto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    destinatario = models.CharField(max_length=255, null=True, blank=True)
    pagado = models.BooleanField(default=False, null=True, blank=True)
    forma_pago = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=100, null=True, blank=True)
    fecha_pago_limite = models.DateField(null=True, blank=True)
    es_cobro = models.BooleanField(default=False, null=True, blank=True)
    cobrar_a = models.CharField(max_length=255, null=True, blank=True)
    id_trabajo = models.ForeignKey(Trabajo, on_delete=models.SET_NULL, null=True, blank=True, related_name='costos', db_column='id_trabajo')
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'costos'


class Factura(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='facturas', null=True, blank=True)
    numero = models.CharField(max_length=100, unique=True, null=True, blank=True)
    fecha_emision = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    estado = models.CharField(max_length=50, default='Pendiente', null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facturas'


class FacturaItem(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    cantidad = models.IntegerField(default=1, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'factura_items'


class Credito(models.Model):
    entidad = models.CharField(max_length=255, null=True, blank=True)
    monto_otorgado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tasa_interes_anual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    plazo_meses = models.IntegerField(null=True, blank=True)
    fecha_desembolso = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, default='Activo', null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creditos'


class CuotaCredito(models.Model):
    credito = models.ForeignKey(Credito, on_delete=models.CASCADE, related_name='cuotas', db_column='id_credito', null=True, blank=True)
    numero_cuota = models.IntegerField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=50, default='Pendiente', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cuotas_credito'
        unique_together = ('credito', 'numero_cuota')


class Pago(models.Model):
    monto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    id_factura = models.ForeignKey(Factura, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos', db_column='id_factura')
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pagos'


class Movimiento(models.Model):
    monto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=100, null=True, blank=True)
    pagado = models.BooleanField(default=False, null=True, blank=True)
    forma_pago = models.CharField(max_length=50, null=True, blank=True)
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)
    es_cobro = models.BooleanField(default=False, null=True, blank=True)
    destinatario = models.CharField(max_length=255, null=True, blank=True)
    cobrar_a = models.CharField(max_length=255, null=True, blank=True)
    fecha_pago_limite = models.DateField(null=True, blank=True)
    id_trabajo = models.ForeignKey(Trabajo, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_trabajo')
    id_factura = models.ForeignKey(Factura, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_factura')
    fecha_pago = models.DateField(null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movimientos'


class Mantenimiento(models.Model):
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='mantenimientos', db_column='id_maquina', null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=50, default='Pendiente', null=True, blank=True)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mantenimientos'


class Insumo(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    categoria = models.CharField(max_length=100, null=True, blank=True)
    unidad = models.CharField(max_length=50, null=True, blank=True)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    proveedor = models.CharField(max_length=255, null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True, null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'insumos'

