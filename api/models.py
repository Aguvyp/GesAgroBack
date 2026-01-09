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
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    # password viene de AbstractBaseUser
    rol = models.CharField(max_length=50, choices=ROLES, default='Operario')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Mapear is_active a activo (que existe en la BD)
    is_active = models.BooleanField(default=True, db_column='activo')
    
    # Sobrescribir last_login de AbstractBaseUser y mapearlo a ultimo_acceso que existe en la BD
    last_login = models.DateTimeField(null=True, blank=True, db_column='ultimo_acceso')

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.email

class TipoTrabajo(models.Model):
    trabajo = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tipo_trabajo'


    def __str__(self):
        return self.trabajo

class Campo(models.Model):
    nombre = models.CharField(max_length=255)
    hectareas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    detalles = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campos'

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.CharField(max_length=500, null=True, blank=True)
    cuit = models.CharField(max_length=20, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clientes'


    def __str__(self):
        return self.nombre

class CampoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='campos_asignados')
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='clientes_asignados')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campos_cliente'
        unique_together = ('cliente', 'campo', 'activo')


class Maquina(models.Model):
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    ano = models.IntegerField()
    detalles = models.TextField(null=True, blank=True)
    ancho_trabajo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=50, default='Disponible', null=True, blank=True)
    superficie_total_ha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ultimo_trabajo = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'maquinas'


    def __str__(self):
        return self.nombre

class Personal(models.Model):
    nombre = models.CharField(max_length=255)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    superficie_total_ha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    trabajos_completados = models.IntegerField(default=0)
    ultimo_trabajo = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Campo usuario comentado porque la columna no existe en la base de datos
    # usuario = models.OneToOneField(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_info')

    class Meta:
        db_table = 'personal'


    def __str__(self):
        return self.nombre

class Trabajo(models.Model):
    id_tipo_trabajo = models.ForeignKey(TipoTrabajo, on_delete=models.PROTECT, related_name='trabajos', db_column='id_tipo_trabajo')
    cultivo = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='trabajos')
    estado = models.CharField(max_length=50, default='Pendiente', null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    a_terceros = models.BooleanField(default=False)
    cobrado = models.BooleanField(default=False)
    monto_cobrado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cliente = models.CharField(max_length=255, null=True, blank=True)
    servicio_contratado = models.BooleanField(default=False)
    rinde_cosecha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    humedad_cosecha = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    personal = models.ManyToManyField(Personal, through='TrabajoPersonal', related_name='trabajos')
    maquinas = models.ManyToManyField(Maquina, through='TrabajoMaquina', related_name='trabajos')

    class Meta:
        db_table = 'trabajos'


class TrabajoPersonal(models.Model):
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE)
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    hectareas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    horas_trabajadas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trabajo_personal'
        unique_together = ('trabajo', 'personal')


class TrabajoMaquina(models.Model):
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trabajo_maquinas'
        unique_together = ('trabajo', 'maquina')


class Costo(models.Model):
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    destinatario = models.CharField(max_length=255)
    pagado = models.BooleanField(default=False)
    forma_pago = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=100, null=True, blank=True)
    fecha_pago_limite = models.DateField(null=True, blank=True)
    es_cobro = models.BooleanField(default=False)
    cobrar_a = models.CharField(max_length=255, null=True, blank=True)
    id_trabajo = models.ForeignKey(Trabajo, on_delete=models.SET_NULL, null=True, blank=True, related_name='costos', db_column='id_trabajo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'costos'


class Factura(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='facturas')
    numero = models.CharField(max_length=100, unique=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=50, default='Pendiente')
    observaciones = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facturas'


class FacturaItem(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='items')
    descripcion = models.CharField(max_length=500)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'factura_items'


class Credito(models.Model):
    entidad = models.CharField(max_length=255)
    monto_otorgado = models.DecimalField(max_digits=12, decimal_places=2)
    tasa_interes_anual = models.DecimalField(max_digits=5, decimal_places=2)
    plazo_meses = models.IntegerField()
    fecha_desembolso = models.DateField()
    estado = models.CharField(max_length=50, default='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creditos'


class CuotaCredito(models.Model):
    credito = models.ForeignKey(Credito, on_delete=models.CASCADE, related_name='cuotas', db_column='id_credito')
    numero_cuota = models.IntegerField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=50, default='Pendiente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cuotas_credito'
        unique_together = ('credito', 'numero_cuota')


class Pago(models.Model):
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    metodo_pago = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    id_factura = models.ForeignKey(Factura, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos', db_column='id_factura')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pagos'


class Movimiento(models.Model):
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=100, null=True, blank=True)
    pagado = models.BooleanField(default=False)
    forma_pago = models.CharField(max_length=50, null=True, blank=True)
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)
    es_cobro = models.BooleanField(default=False)
    destinatario = models.CharField(max_length=255, null=True, blank=True)
    cobrar_a = models.CharField(max_length=255, null=True, blank=True)
    fecha_pago_limite = models.DateField(null=True, blank=True)
    id_trabajo = models.ForeignKey(Trabajo, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_trabajo')
    id_factura = models.ForeignKey(Factura, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_factura')
    fecha_pago = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movimientos'


class Mantenimiento(models.Model):
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='mantenimientos', db_column='id_maquina')
    fecha = models.DateField()
    descripcion = models.TextField()
    estado = models.CharField(max_length=50, default='Pendiente')
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mantenimientos'


class Insumo(models.Model):
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    unidad = models.CharField(max_length=50)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    proveedor = models.CharField(max_length=255, null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'insumos'

