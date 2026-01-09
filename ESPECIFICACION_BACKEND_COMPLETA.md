# ESPECIFICACIÓN COMPLETA DEL BACKEND PARA GESAGRO FRONTEND

## ÍNDICE
1. [Configuración General](#configuración-general)
2. [Autenticación](#autenticación)
3. [Endpoints por Módulo](#endpoints-por-módulo)
4. [Modelos de Datos](#modelos-de-datos)
5. [Formatos de Request y Response](#formatos-de-request-y-response)
6. [Endpoints Optimizados Flutter](#endpoints-optimizados-flutter)
7. [Endpoints de Dashboard y Reportes](#endpoints-de-dashboard-y-reportes)

---

## CONFIGURACIÓN GENERAL

### Base URL
```
https://59d7039eff24.ngrok-free.app
```

### Headers Requeridos
- **Content-Type**: `application/json; charset=utf-8`
- **Accept**: `application/json`
- **Authorization**: `Bearer {token}` (requerido para todos los endpoints excepto `/api/auth/*` y `/api/health/`)

### Timeout
- **Timeout de conexión**: 30 segundos
- **Timeout de recepción**: 30 segundos
- **Timeout de envío**: 30 segundos

### Formato de Fechas
- **Formato estándar**: `YYYY-MM-DD` (ejemplo: `2024-01-15`)
- **Formato ISO8601 completo**: `YYYY-MM-DDTHH:mm:ss` (para campos opcionales con hora)

---

## AUTENTICACIÓN

### 1. POST `/api/auth/login/`
**Descripción**: Iniciar sesión y obtener token JWT

**Request Body**:
```json
{
  "email": "usuario@example.com",
  "password": "password123"
}
```

**Response 200 OK**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "Administrador",
  "user_id": 1,
  "personal_id": 1,
  "usuario_id": 1
}
```

**Response 401 Unauthorized**:
```json
{
  "detail": "Credenciales inválidas"
}
```

---

### 2. POST `/api/auth/register/`
**Descripción**: Registrar nuevo usuario

**Request Body**:
```json
{
  "nombre": "Juan Pérez",
  "dni": "12345678",
  "telefono": "+5491123456789",
  "email": "juan@example.com",
  "password": "password123"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "role": "Operario",
  "message": "Usuario registrado exitosamente"
}
```

**Response 400 Bad Request**:
```json
{
  "detail": "El email ya está registrado"
}
```

---

### 3. GET `/api/auth/test/`
**Descripción**: Test de conexión (sin autenticación)

**Response 200 OK**:
```json
{
  "status": "ok",
  "message": "Conexión exitosa"
}
```

---

### 4. GET `/api/health/`
**Descripción**: Health check del servidor (sin autenticación)

**Response 200 OK**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## ENDPOINTS POR MÓDULO

### USUARIOS

#### GET `/api/usuarios/`
**Descripción**: Listar usuarios con paginación

**Query Parameters**:
- `skip` (int, opcional): Número de registros a saltar (default: 0)
- `limit` (int, opcional): Número máximo de registros (default: 100)

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "rol": "Administrador",
    "activo": true,
    "fecha_creacion": "2024-01-01T00:00:00Z",
    "ultimo_acceso": "2024-01-15T10:30:00Z"
  }
]
```

---

#### GET `/api/usuarios/{id}`
**Descripción**: Obtener usuario por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "rol": "Administrador",
  "activo": true,
  "fecha_creacion": "2024-01-01T00:00:00Z",
  "ultimo_acceso": "2024-01-15T10:30:00Z"
}
```

---

#### POST `/api/usuarios/create`
**Descripción**: Crear nuevo usuario

**Request Body**:
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "rol": "Operario",
  "password": "password123"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "rol": "Operario",
  "activo": true,
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "ultimo_acceso": null
}
```

---

#### PUT `/api/usuarios/{id}/update`
**Descripción**: Actualizar usuario

**Request Body**:
```json
{
  "nombre": "Juan Pérez Actualizado",
  "email": "juan.nuevo@example.com",
  "rol": "Contable",
  "activo": true
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Juan Pérez Actualizado",
  "email": "juan.nuevo@example.com",
  "rol": "Contable",
  "activo": true,
  "fecha_creacion": "2024-01-01T00:00:00Z",
  "ultimo_acceso": "2024-01-15T10:30:00Z"
}
```

---

#### DELETE `/api/usuarios/{id}/delete`
**Descripción**: Eliminar usuario

**Response 200 OK**:
```json
{
  "message": "Usuario eliminado exitosamente"
}
```

---

### CAMPOS

#### GET `/api/campos/`
**Descripción**: Listar campos con paginación

**Query Parameters**:
- `skip` (int, opcional): Número de registros a saltar (default: 0)
- `limit` (int, opcional): Número máximo de registros (default: 100)

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "nombre": "Campo Norte",
    "hectareas": 50.5,
    "latitud": -34.603722,
    "longitud": -58.381592,
    "detalles": "Campo principal de siembra"
  }
]
```

---

#### GET `/api/campos/{id}`
**Descripción**: Obtener campo por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Campo Norte",
  "hectareas": 50.5,
  "latitud": -34.603722,
  "longitud": -58.381592,
  "detalles": "Campo principal de siembra"
}
```

---

#### POST `/api/campos/create`
**Descripción**: Crear nuevo campo

**Request Body**:
```json
{
  "nombre": "Campo Sur",
  "hectareas": 30.0,
  "latitud": -34.603722,
  "longitud": -58.381592,
  "detalles": "Campo secundario"
}
```

**Response 201 Created**:
```json
{
  "id": 2,
  "nombre": "Campo Sur",
  "hectareas": 30.0,
  "latitud": -34.603722,
  "longitud": -58.381592,
  "detalles": "Campo secundario"
}
```

---

#### PUT `/api/campos/{id}/update`
**Descripción**: Actualizar campo

**Request Body**:
```json
{
  "nombre": "Campo Sur Actualizado",
  "hectareas": 35.0,
  "latitud": -34.603722,
  "longitud": -58.381592,
  "detalles": "Campo secundario actualizado"
}
```

**Response 200 OK**:
```json
{
  "id": 2,
  "nombre": "Campo Sur Actualizado",
  "hectareas": 35.0,
  "latitud": -34.603722,
  "longitud": -58.381592,
  "detalles": "Campo secundario actualizado"
}
```

---

#### DELETE `/api/campos/{id}/delete`
**Descripción**: Eliminar campo

**Response 200 OK**:
```json
{
  "message": "Campo eliminado exitosamente"
}
```

---

### CLIENTES

#### GET `/api/clientes/`
**Descripción**: Listar todos los clientes

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "nombre": "Agro S.A.",
    "email": "contacto@agro.com",
    "telefono": "+5491123456789",
    "direccion": "Av. Principal 123",
    "cuit": "20-12345678-9",
    "observaciones": "Cliente principal",
    "fecha_creacion": "2024-01-01T00:00:00Z",
    "fecha_modificacion": "2024-01-15T10:30:00Z"
  }
]
```

---

#### GET `/api/clientes/{id}`
**Descripción**: Obtener cliente por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Agro S.A.",
  "email": "contacto@agro.com",
  "telefono": "+5491123456789",
  "direccion": "Av. Principal 123",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente principal",
  "fecha_creacion": "2024-01-01T00:00:00Z",
  "fecha_modificacion": "2024-01-15T10:30:00Z"
}
```

---

#### POST `/api/clientes/create`
**Descripción**: Crear nuevo cliente

**Request Body**:
```json
{
  "nombre": "Agro S.A.",
  "email": "contacto@agro.com",
  "telefono": "+5491123456789",
  "direccion": "Av. Principal 123",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente principal"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "nombre": "Agro S.A.",
  "email": "contacto@agro.com",
  "telefono": "+5491123456789",
  "direccion": "Av. Principal 123",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente principal",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_modificacion": "2024-01-15T10:30:00Z"
}
```

---

#### PUT `/api/clientes/{id}/update`
**Descripción**: Actualizar cliente

**Request Body**:
```json
{
  "nombre": "Agro S.A. Actualizado",
  "email": "nuevo@agro.com",
  "telefono": "+5491123456789",
  "direccion": "Av. Principal 456",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente principal actualizado"
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Agro S.A. Actualizado",
  "email": "nuevo@agro.com",
  "telefono": "+5491123456789",
  "direccion": "Av. Principal 456",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente principal actualizado",
  "fecha_creacion": "2024-01-01T00:00:00Z",
  "fecha_modificacion": "2024-01-15T10:30:00Z"
}
```

---

#### DELETE `/api/clientes/{id}/delete`
**Descripción**: Eliminar cliente

**Response 200 OK**:
```json
{
  "message": "Cliente eliminado exitosamente"
}
```

---

### CAMPOS-CLIENTE (Asignaciones)

#### GET `/api/campos-cliente/`
**Descripción**: Listar todas las asignaciones de campos a clientes

**Query Parameters**:
- `cliente_id` (int, opcional): Filtrar por cliente específico

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "cliente_id": 1,
    "campo_id": 1,
    "fecha_asignacion": "2024-01-01T00:00:00Z",
    "observaciones": "Asignación inicial",
    "activo": true
  }
]
```

---

#### GET `/api/campos-cliente/{id}`
**Descripción**: Obtener asignación por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "cliente_id": 1,
  "campo_id": 1,
  "fecha_asignacion": "2024-01-01T00:00:00Z",
  "observaciones": "Asignación inicial",
  "activo": true
}
```

---

#### POST `/api/campos-cliente/create`
**Descripción**: Asignar campo a cliente

**Request Body**:
```json
{
  "cliente_id": 1,
  "campo_id": 1,
  "observaciones": "Asignación inicial",
  "activo": true
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "cliente_id": 1,
  "campo_id": 1,
  "fecha_asignacion": "2024-01-15T10:30:00Z",
  "observaciones": "Asignación inicial",
  "activo": true
}
```

---

#### PUT `/api/campos-cliente/{id}/update`
**Descripción**: Actualizar asignación

**Request Body**:
```json
{
  "observaciones": "Asignación actualizada",
  "activo": true
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "cliente_id": 1,
  "campo_id": 1,
  "fecha_asignacion": "2024-01-01T00:00:00Z",
  "observaciones": "Asignación actualizada",
  "activo": true
}
```

---

#### DELETE `/api/campos-cliente/{id}/delete`
**Descripción**: Eliminar asignación (hard delete)

**Response 200 OK**:
```json
{
  "message": "Asignación eliminada exitosamente"
}
```

---

#### PATCH `/api/campos-cliente/{id}/desactivar`
**Descripción**: Desactivar asignación (soft delete)

**Response 200 OK**:
```json
{
  "id": 1,
  "cliente_id": 1,
  "campo_id": 1,
  "fecha_asignacion": "2024-01-01T00:00:00Z",
  "observaciones": "Asignación inicial",
  "activo": false
}
```

---

### MÁQUINAS

#### GET `/api/maquinas/`
**Descripción**: Listar todas las máquinas

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "nombre": "Tractor John Deere",
    "marca": "John Deere",
    "modelo": "6120M",
    "ano": 2020,
    "detalles": "Tractor principal",
    "ancho_trabajo": 3.5,
    "estado": "Disponible",
    "superficie_total_ha": 150.5,
    "horas_trabajadas": 250.0,
    "ultimo_trabajo": "Siembra Campo Norte"
  }
]
```

---

#### GET `/api/maquinas/{id}`
**Descripción**: Obtener máquina por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Tractor John Deere",
  "marca": "John Deere",
  "modelo": "6120M",
  "ano": 2020,
  "detalles": "Tractor principal",
  "ancho_trabajo": 3.5,
  "estado": "Disponible",
  "superficie_total_ha": 150.5,
  "horas_trabajadas": 250.0,
  "ultimo_trabajo": "Siembra Campo Norte"
}
```

---

#### POST `/api/maquinas/create`
**Descripción**: Crear nueva máquina

**Request Body**:
```json
{
  "nombre": "Tractor John Deere",
  "marca": "John Deere",
  "modelo": "6120M",
  "ano": 2020,
  "detalles": "Tractor principal",
  "ancho_trabajo": 3.5,
  "estado": "Disponible"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "nombre": "Tractor John Deere",
  "marca": "John Deere",
  "modelo": "6120M",
  "ano": 2020,
  "detalles": "Tractor principal",
  "ancho_trabajo": 3.5,
  "estado": "Disponible",
  "superficie_total_ha": 0.0,
  "horas_trabajadas": 0.0,
  "ultimo_trabajo": null
}
```

---

#### PUT `/api/maquinas/{id}/update`
**Descripción**: Actualizar máquina

**Request Body**:
```json
{
  "nombre": "Tractor John Deere Actualizado",
  "marca": "John Deere",
  "modelo": "6120M",
  "ano": 2020,
  "detalles": "Tractor principal actualizado",
  "ancho_trabajo": 3.5,
  "estado": "En uso"
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Tractor John Deere Actualizado",
  "marca": "John Deere",
  "modelo": "6120M",
  "ano": 2020,
  "detalles": "Tractor principal actualizado",
  "ancho_trabajo": 3.5,
  "estado": "En uso",
  "superficie_total_ha": 150.5,
  "horas_trabajadas": 250.0,
  "ultimo_trabajo": "Siembra Campo Norte"
}
```

---

#### DELETE `/api/maquinas/{id}/delete`
**Descripción**: Eliminar máquina

**Response 200 OK**:
```json
{
  "message": "Máquina eliminada exitosamente"
}
```

---

### PERSONAL

#### GET `/api/personal/`
**Descripción**: Listar todo el personal

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "dni": "12345678",
    "telefono": "+5491123456789",
    "superficie_total_ha": 200.5,
    "horas_trabajadas": 150.0,
    "trabajos_completados": 5,
    "ultimo_trabajo": "Siembra Campo Norte"
  }
]
```

---

#### GET `/api/personal/{id}`
**Descripción**: Obtener personal por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "dni": "12345678",
  "telefono": "+5491123456789",
  "superficie_total_ha": 200.5,
  "horas_trabajadas": 150.0,
  "trabajos_completados": 5,
  "ultimo_trabajo": "Siembra Campo Norte"
}
```

---

#### POST `/api/personal/create`
**Descripción**: Crear nuevo personal

**Request Body**:
```json
{
  "nombre": "Juan Pérez",
  "dni": "12345678",
  "telefono": "+5491123456789"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "dni": "12345678",
  "telefono": "+5491123456789",
  "superficie_total_ha": 0.0,
  "horas_trabajadas": 0.0,
  "trabajos_completados": 0,
  "ultimo_trabajo": null
}
```

---

#### PUT `/api/personal/{id}/update`
**Descripción**: Actualizar personal

**Request Body**:
```json
{
  "nombre": "Juan Pérez Actualizado",
  "dni": "12345678",
  "telefono": "+5491123456789"
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Juan Pérez Actualizado",
  "dni": "12345678",
  "telefono": "+5491123456789",
  "superficie_total_ha": 200.5,
  "horas_trabajadas": 150.0,
  "trabajos_completados": 5,
  "ultimo_trabajo": "Siembra Campo Norte"
}
```

---

#### DELETE `/api/personal/{id}/delete`
**Descripción**: Eliminar personal

**Response 200 OK**:
```json
{
  "message": "Personal eliminado exitosamente"
}
```

---

#### GET `/api/personal/validate-dni`
**Descripción**: Validar si un DNI está disponible

**Query Parameters**:
- `dni` (string, requerido): DNI a validar
- `exclude_id` (int, opcional): ID a excluir de la validación (útil para actualizaciones)

**Response 200 OK**:
```json
{
  "available": true
}
```

**Response 200 OK (DNI duplicado)**:
```json
{
  "available": false
}
```

---

### TRABAJOS

#### GET `/api/trabajos/`
**Descripción**: Listar todos los trabajos

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "id_tipo_trabajo": 1,
    "tipo": "Siembra",
    "cultivo": "Soja",
    "fecha_inicio": "2024-01-15",
    "fecha_fin": "2024-01-20",
    "id_personal": [1, 2],
    "id_maquinas": [1, 2],
    "campo_id": 1,
    "campo_nombre": "Campo Norte",
    "campo_ha": 50.5,
    "estado": "Completado",
    "observaciones": "Trabajo completado exitosamente",
    "a_terceros": false,
    "cobrado": true,
    "monto_cobrado": 50000.0,
    "cliente": null,
    "servicio_contratado": false,
    "rinde_cosecha": 0.0,
    "humedad_cosecha": 0.0
  }
]
```

**NOTA IMPORTANTE**: El campo `tipo` debe contener el nombre del tipo de trabajo (ej: "Siembra", "Cosecha", etc.). El frontend espera recibir el nombre en este campo aunque también se envíe `id_tipo_trabajo`.

---

#### GET `/api/trabajos/{id}`
**Descripción**: Obtener trabajo por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "id_tipo_trabajo": 1,
  "tipo": "Siembra",
  "cultivo": "Soja",
  "fecha_inicio": "2024-01-15",
  "fecha_fin": "2024-01-20",
  "id_personal": [1, 2],
  "id_maquinas": [1, 2],
  "campo_id": 1,
  "campo_nombre": "Campo Norte",
  "campo_ha": 50.5,
  "estado": "Completado",
  "observaciones": "Trabajo completado exitosamente",
  "a_terceros": false,
  "cobrado": true,
  "monto_cobrado": 50000.0,
  "cliente": null,
  "servicio_contratado": false,
  "rinde_cosecha": 0.0,
  "humedad_cosecha": 0.0
}
```

---

#### GET `/api/trabajos/detalle/{id}`
**Descripción**: Obtener detalle completo de un trabajo (incluye campo, cliente, personal con hectáreas y máquinas)

**Response 200 OK**:
```json
{
  "id": 1,
  "tipo": "Siembra",
  "cliente": "Agro S.A.",
  "cultivo": "Soja",
  "observaciones": "Trabajo completado exitosamente",
  "estado": "Completado",
  "a_terceros": false,
  "fecha_inicio": "2024-01-15",
  "fecha_fin": "2024-01-20",
  "campo_id": 1,
  "campo": {
    "id": 1,
    "nombre": "Campo Norte",
    "hectareas": 50.5,
    "latitud": -34.603722,
    "longitud": -58.381592,
    "detalles": "Campo principal de siembra"
  },
  "cliente_info": {
    "id": 1,
    "nombre_razon_social": "Agro S.A.",
    "cuit": "20-12345678-9",
    "direccion": "Av. Principal 123",
    "telefono": "+5491123456789",
    "email": "contacto@agro.com"
  },
  "maquinas": [
    {
      "id": 1,
      "nombre": "Tractor John Deere",
      "marca": "John Deere",
      "modelo": "6120M"
    }
  ],
  "personal": [
    {
      "id": 1,
      "nombre": "Juan Pérez",
      "dni": "12345678",
      "rol": "Operario",
      "ha": 25.5
    },
    {
      "id": 2,
      "nombre": "María García",
      "dni": "87654321",
      "rol": "Operario",
      "ha": 25.0
    }
  ],
  "cobrado": true,
  "monto_cobrado": 50000.0
}
```

**NOTA CRÍTICA**: El campo `personal` debe incluir el campo `ha` (hectáreas trabajadas por cada operario en este trabajo específico). Este es un dato diferente a `superficie_total_ha` del personal.

---

#### POST `/api/trabajos/create`
**Descripción**: Crear nuevo trabajo

**Request Body**:
```json
{
  "id_tipo_trabajo": 1,
  "cliente": "Agro S.A.",
  "fecha_inicio": "2024-01-15",
  "id_campo": 1,
  "cultivo": "Soja",
  "observaciones": "Trabajo nuevo",
  "estado": "Pendiente",
  "a_terceros": false,
  "servicio_contratado": false,
  "fecha_fin": "2024-01-20",
  "rinde_cosecha": 0.0,
  "humedad_cosecha": 0.0,
  "id_personal": [1, 2],
  "id_maquinas": [1, 2],
  "personal_hectareas": [
    {
      "id": 1,
      "ha": 25.5
    },
    {
      "id": 2,
      "ha": 25.0
    }
  ]
}
```

**NOTA IMPORTANTE**: 
- Si `id_tipo_trabajo == 1` (Cosecha), los campos `rinde_cosecha` y `humedad_cosecha` pueden tener valores reales o ser null.
- Si `id_tipo_trabajo != 1`, estos campos deben ser `0.0`.
- El campo `personal_hectareas` es un array de objetos con `id` (del personal) y `ha` (hectáreas trabajadas). Este campo es OPCIONAL pero RECOMENDADO para mantener la consistencia de datos.

**Response 201 Created**:
```json
{
  "id": 1,
  "id_tipo_trabajo": 1,
  "tipo": "Siembra",
  "cultivo": "Soja",
  "fecha_inicio": "2024-01-15",
  "fecha_fin": "2024-01-20",
  "id_personal": [1, 2],
  "id_maquinas": [1, 2],
  "campo_id": 1,
  "campo_nombre": "Campo Norte",
  "campo_ha": 50.5,
  "estado": "Pendiente",
  "observaciones": "Trabajo nuevo",
  "a_terceros": false,
  "cobrado": false,
  "monto_cobrado": null,
  "cliente": "Agro S.A.",
  "servicio_contratado": false,
  "rinde_cosecha": 0.0,
  "humedad_cosecha": 0.0
}
```

---

#### PUT `/api/trabajos/{id}/update`
**Descripción**: Actualizar trabajo

**Request Body**:
```json
{
  "id_tipo_trabajo": 1,
  "cliente": "Agro S.A.",
  "fecha_inicio": "2024-01-15",
  "id_campo": 1,
  "cultivo": "Soja",
  "observaciones": "Trabajo actualizado",
  "estado": "En curso",
  "a_terceros": false,
  "servicio_contratado": false,
  "fecha_fin": "2024-01-20",
  "rinde_cosecha": 0.0,
  "humedad_cosecha": 0.0,
  "id_personal": [1, 2],
  "id_maquinas": [1, 2],
  "cobrado": true,
  "monto_cobrado": 50000.0
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "id_tipo_trabajo": 1,
  "tipo": "Siembra",
  "cultivo": "Soja",
  "fecha_inicio": "2024-01-15",
  "fecha_fin": "2024-01-20",
  "id_personal": [1, 2],
  "id_maquinas": [1, 2],
  "campo_id": 1,
  "campo_nombre": "Campo Norte",
  "campo_ha": 50.5,
  "estado": "En curso",
  "observaciones": "Trabajo actualizado",
  "a_terceros": false,
  "cobrado": true,
  "monto_cobrado": 50000.0,
  "cliente": "Agro S.A.",
  "servicio_contratado": false,
  "rinde_cosecha": 0.0,
  "humedad_cosecha": 0.0
}
```

---

#### DELETE `/api/trabajos/{id}/delete`
**Descripción**: Eliminar trabajo

**Response 200 OK**:
```json
{
  "message": "Trabajo eliminado exitosamente"
}
```

---

### TIPOS DE TRABAJO

#### GET `/api/tipo-trabajo/`
**Descripción**: Listar todos los tipos de trabajo

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "trabajo": "Siembra"
  },
  {
    "id": 2,
    "trabajo": "Cosecha"
  },
  {
    "id": 3,
    "trabajo": "Laboreo"
  }
]
```

---

#### GET `/api/tipo-trabajo/{id}`
**Descripción**: Obtener tipo de trabajo por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "trabajo": "Siembra"
}
```

---

#### POST `/api/tipo-trabajo/create`
**Descripción**: Crear nuevo tipo de trabajo

**Request Body**:
```json
{
  "trabajo": "Pulverización"
}
```

**Response 201 Created**:
```json
{
  "id": 4,
  "trabajo": "Pulverización"
}
```

---

#### PUT `/api/tipo-trabajo/{id}/update`
**Descripción**: Actualizar tipo de trabajo

**Request Body**:
```json
{
  "trabajo": "Pulverización Actualizada"
}
```

**Response 200 OK**:
```json
{
  "id": 4,
  "trabajo": "Pulverización Actualizada"
}
```

---

#### DELETE `/api/tipo-trabajo/{id}/delete`
**Descripción**: Eliminar tipo de trabajo

**Response 200 OK**:
```json
{
  "message": "Tipo de trabajo eliminado exitosamente"
}
```

---

### COSTOS

#### GET `/api/costos/`
**Descripción**: Listar todos los costos

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "monto": 5000.0,
    "fecha": "2024-01-15",
    "destinatario": "Proveedor ABC",
    "pagado": true,
    "forma_pago": "Transferencia",
    "descripcion": "Compra de semillas",
    "categoria": "Semillas",
    "fecha_pago_limite": "2024-01-20",
    "es_cobro": false,
    "cobrar_a": null,
    "id_trabajo": null
  }
]
```

---

#### GET `/api/costos/{id}`
**Descripción**: Obtener costo por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "monto": 5000.0,
  "fecha": "2024-01-15",
  "destinatario": "Proveedor ABC",
  "pagado": true,
  "forma_pago": "Transferencia",
  "descripcion": "Compra de semillas",
  "categoria": "Semillas",
  "fecha_pago_limite": "2024-01-20",
  "es_cobro": false,
  "cobrar_a": null,
  "id_trabajo": null
}
```

---

#### POST `/api/costos/create`
**Descripción**: Crear nuevo costo

**Request Body**:
```json
{
  "monto": 5000.0,
  "fecha": "2024-01-15",
  "destinatario": "Proveedor ABC",
  "pagado": false,
  "forma_pago": "Transferencia",
  "descripcion": "Compra de semillas",
  "categoria": "Semillas",
  "fecha_pago_limite": "2024-01-20",
  "es_cobro": false,
  "cobrar_a": null,
  "id_trabajo": null
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "monto": 5000.0,
  "fecha": "2024-01-15",
  "destinatario": "Proveedor ABC",
  "pagado": false,
  "forma_pago": "Transferencia",
  "descripcion": "Compra de semillas",
  "categoria": "Semillas",
  "fecha_pago_limite": "2024-01-20",
  "es_cobro": false,
  "cobrar_a": null,
  "id_trabajo": null
}
```

---

#### PUT `/api/costos/{id}/update`
**Descripción**: Actualizar costo

**Request Body**:
```json
{
  "monto": 5500.0,
  "fecha": "2024-01-15",
  "destinatario": "Proveedor ABC",
  "pagado": true,
  "forma_pago": "Transferencia",
  "descripcion": "Compra de semillas actualizada",
  "categoria": "Semillas",
  "fecha_pago_limite": "2024-01-20",
  "es_cobro": false,
  "cobrar_a": null,
  "id_trabajo": null
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "monto": 5500.0,
  "fecha": "2024-01-15",
  "destinatario": "Proveedor ABC",
  "pagado": true,
  "forma_pago": "Transferencia",
  "descripcion": "Compra de semillas actualizada",
  "categoria": "Semillas",
  "fecha_pago_limite": "2024-01-20",
  "es_cobro": false,
  "cobrar_a": null,
  "id_trabajo": null
}
```

---

#### DELETE `/api/costos/{id}/delete`
**Descripción**: Eliminar costo

**Response 200 OK**:
```json
{
  "message": "Costo eliminado exitosamente"
}
```

---

#### GET `/api/costos/pagados`
**Descripción**: Listar costos pagados

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "monto": 5000.0,
    "fecha": "2024-01-15",
    "destinatario": "Proveedor ABC",
    "pagado": true,
    "forma_pago": "Transferencia",
    "descripcion": "Compra de semillas",
    "categoria": "Semillas",
    "fecha_pago_limite": "2024-01-20",
    "es_cobro": false,
    "cobrar_a": null,
    "id_trabajo": null
  }
]
```

---

#### GET `/api/costos/pendientes`
**Descripción**: Listar costos pendientes

**Response 200 OK**:
```json
[
  {
    "id": 2,
    "monto": 3000.0,
    "fecha": "2024-01-15",
    "destinatario": "Proveedor XYZ",
    "pagado": false,
    "forma_pago": "Efectivo",
    "descripcion": "Compra de fertilizantes",
    "categoria": "Fertilizantes",
    "fecha_pago_limite": "2024-01-25",
    "es_cobro": false,
    "cobrar_a": null,
    "id_trabajo": null
  }
]
```

---

### FACTURAS

#### GET `/api/facturas/`
**Descripción**: Listar todas las facturas

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "cliente_id": 1,
    "numero": "FAC-001",
    "fecha_emision": "2024-01-15",
    "fecha_vencimiento": "2024-02-15",
    "monto_total": 100000.0,
    "monto_pagado": 50000.0,
    "estado": "Pendiente",
    "observaciones": "Factura pendiente de pago",
    "items": [
      {
        "id": 1,
        "descripcion": "Servicio de siembra",
        "cantidad": 1,
        "precio_unitario": 100000.0,
        "subtotal": 100000.0
      }
    ]
  }
]
```

---

#### GET `/api/facturas/{id}`
**Descripción**: Obtener factura por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "cliente_id": 1,
  "numero": "FAC-001",
  "fecha_emision": "2024-01-15",
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 100000.0,
  "monto_pagado": 50000.0,
  "estado": "Pendiente",
  "observaciones": "Factura pendiente de pago",
  "items": [
    {
      "id": 1,
      "descripcion": "Servicio de siembra",
      "cantidad": 1,
      "precio_unitario": 100000.0,
      "subtotal": 100000.0
    }
  ]
}
```

---

#### POST `/api/facturas/create`
**Descripción**: Crear nueva factura

**Request Body**:
```json
{
  "cliente_id": 1,
  "numero": "FAC-001",
  "fecha_emision": "2024-01-15",
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 100000.0,
  "monto_pagado": 0.0,
  "estado": "Pendiente",
  "observaciones": "Factura nueva",
  "items": [
    {
      "descripcion": "Servicio de siembra",
      "cantidad": 1,
      "precio_unitario": 100000.0,
      "subtotal": 100000.0
    }
  ]
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "cliente_id": 1,
  "numero": "FAC-001",
  "fecha_emision": "2024-01-15",
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 100000.0,
  "monto_pagado": 0.0,
  "estado": "Pendiente",
  "observaciones": "Factura nueva",
  "items": [
    {
      "id": 1,
      "descripcion": "Servicio de siembra",
      "cantidad": 1,
      "precio_unitario": 100000.0,
      "subtotal": 100000.0
    }
  ]
}
```

---

#### PUT `/api/facturas/{id}/update`
**Descripción**: Actualizar factura

**Request Body**:
```json
{
  "cliente_id": 1,
  "numero": "FAC-001",
  "fecha_emision": "2024-01-15",
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 100000.0,
  "monto_pagado": 50000.0,
  "estado": "Pendiente",
  "observaciones": "Factura parcialmente pagada",
  "items": [
    {
      "id": 1,
      "descripcion": "Servicio de siembra",
      "cantidad": 1,
      "precio_unitario": 100000.0,
      "subtotal": 100000.0
    }
  ]
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "cliente_id": 1,
  "numero": "FAC-001",
  "fecha_emision": "2024-01-15",
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 100000.0,
  "monto_pagado": 50000.0,
  "estado": "Pendiente",
  "observaciones": "Factura parcialmente pagada",
  "items": [
    {
      "id": 1,
      "descripcion": "Servicio de siembra",
      "cantidad": 1,
      "precio_unitario": 100000.0,
      "subtotal": 100000.0
    }
  ]
}
```

---

#### DELETE `/api/facturas/{id}/delete`
**Descripción**: Eliminar factura

**Response 200 OK**:
```json
{
  "message": "Factura eliminada exitosamente"
}
```

---

### CRÉDITOS

#### GET `/api/creditos/`
**Descripción**: Listar todos los créditos

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "entidad": "Banco Nación",
    "monto_otorgado": 500000.0,
    "tasa_interes_anual": 45.5,
    "plazo_meses": 12,
    "fecha_desembolso": "2024-01-15",
    "estado": "Activo"
  }
]
```

---

#### GET `/api/creditos/{id}`
**Descripción**: Obtener crédito por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "entidad": "Banco Nación",
  "monto_otorgado": 500000.0,
  "tasa_interes_anual": 45.5,
  "plazo_meses": 12,
  "fecha_desembolso": "2024-01-15",
  "estado": "Activo"
}
```

---

#### POST `/api/creditos/create`
**Descripción**: Crear nuevo crédito

**Request Body**:
```json
{
  "entidad": "Banco Nación",
  "monto_otorgado": 500000.0,
  "tasa_interes_anual": 45.5,
  "plazo_meses": 12,
  "fecha_desembolso": "2024-01-15",
  "estado": "Activo"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "entidad": "Banco Nación",
  "monto_otorgado": 500000.0,
  "tasa_interes_anual": 45.5,
  "plazo_meses": 12,
  "fecha_desembolso": "2024-01-15",
  "estado": "Activo"
}
```

---

#### PUT `/api/creditos/{id}/update`
**Descripción**: Actualizar crédito

**Request Body**:
```json
{
  "entidad": "Banco Nación",
  "monto_otorgado": 500000.0,
  "tasa_interes_anual": 45.5,
  "plazo_meses": 12,
  "fecha_desembolso": "2024-01-15",
  "estado": "Finalizado"
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "entidad": "Banco Nación",
  "monto_otorgado": 500000.0,
  "tasa_interes_anual": 45.5,
  "plazo_meses": 12,
  "fecha_desembolso": "2024-01-15",
  "estado": "Finalizado"
}
```

---

#### DELETE `/api/creditos/{id}/delete`
**Descripción**: Eliminar crédito

**Response 200 OK**:
```json
{
  "message": "Crédito eliminado exitosamente"
}
```

---

### CUOTAS DE CRÉDITO

#### GET `/api/cuotas-credito/`
**Descripción**: Listar todas las cuotas de crédito

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "id_credito": 1,
    "numero_cuota": 1,
    "fecha_vencimiento": "2024-02-15",
    "monto_total": 50000.0,
    "estado": "Pendiente"
  }
]
```

---

#### GET `/api/cuotas-credito/{id}`
**Descripción**: Obtener cuota de crédito por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "id_credito": 1,
  "numero_cuota": 1,
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 50000.0,
  "estado": "Pendiente"
}
```

---

#### POST `/api/cuotas-credito/create`
**Descripción**: Crear nueva cuota de crédito

**Request Body**:
```json
{
  "id_credito": 1,
  "numero_cuota": 1,
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 50000.0,
  "estado": "Pendiente"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "id_credito": 1,
  "numero_cuota": 1,
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 50000.0,
  "estado": "Pendiente"
}
```

---

#### PUT `/api/cuotas-credito/{id}/update`
**Descripción**: Actualizar cuota de crédito

**Request Body**:
```json
{
  "id_credito": 1,
  "numero_cuota": 1,
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 50000.0,
  "estado": "Pagada"
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "id_credito": 1,
  "numero_cuota": 1,
  "fecha_vencimiento": "2024-02-15",
  "monto_total": 50000.0,
  "estado": "Pagada"
}
```

---

#### DELETE `/api/cuotas-credito/{id}/delete`
**Descripción**: Eliminar cuota de crédito

**Response 200 OK**:
```json
{
  "message": "Cuota de crédito eliminada exitosamente"
}
```

---

### PAGOS

#### GET `/api/pagos/`
**Descripción**: Listar todos los pagos

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "monto": 50000.0,
    "fecha": "2024-01-15",
    "metodo_pago": "Transferencia",
    "descripcion": "Pago de factura",
    "id_factura": 1
  }
]
```

---

#### GET `/api/pagos/{id}`
**Descripción**: Obtener pago por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "metodo_pago": "Transferencia",
  "descripcion": "Pago de factura",
  "id_factura": 1
}
```

---

#### POST `/api/pagos/create`
**Descripción**: Crear nuevo pago

**Request Body**:
```json
{
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "metodo_pago": "Transferencia",
  "descripcion": "Pago de factura",
  "id_factura": 1
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "metodo_pago": "Transferencia",
  "descripcion": "Pago de factura",
  "id_factura": 1
}
```

---

#### PUT `/api/pagos/{id}/update`
**Descripción**: Actualizar pago

**Request Body**:
```json
{
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "metodo_pago": "Efectivo",
  "descripcion": "Pago de factura actualizado",
  "id_factura": 1
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "metodo_pago": "Efectivo",
  "descripcion": "Pago de factura actualizado",
  "id_factura": 1
}
```

---

#### DELETE `/api/pagos/{id}/delete`
**Descripción**: Eliminar pago

**Response 200 OK**:
```json
{
  "message": "Pago eliminado exitosamente"
}
```

---

### MOVIMIENTOS

#### GET `/api/movimientos/`
**Descripción**: Listar todos los movimientos

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "monto": 50000.0,
    "fecha": "2024-01-15",
    "descripcion": "Cobro de trabajo",
    "categoria": "Ingresos",
    "pagado": true,
    "forma_pago": "Transferencia",
    "metodo_pago": "Transferencia",
    "es_cobro": true,
    "destinatario": null,
    "cobrar_a": "Cliente ABC",
    "fecha_pago_limite": null,
    "id_trabajo": 1,
    "id_factura": null,
    "fecha_pago": "2024-01-15",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

---

#### GET `/api/movimientos/{id}`
**Descripción**: Obtener movimiento por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "descripcion": "Cobro de trabajo",
  "categoria": "Ingresos",
  "pagado": true,
  "forma_pago": "Transferencia",
  "metodo_pago": "Transferencia",
  "es_cobro": true,
  "destinatario": null,
  "cobrar_a": "Cliente ABC",
  "fecha_pago_limite": null,
  "id_trabajo": 1,
  "id_factura": null,
  "fecha_pago": "2024-01-15",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### POST `/api/movimientos/create`
**Descripción**: Crear nuevo movimiento

**Request Body**:
```json
{
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "descripcion": "Cobro de trabajo",
  "categoria": "Ingresos",
  "pagado": true,
  "forma_pago": "Transferencia",
  "es_cobro": true,
  "destinatario": null,
  "cobrar_a": "Cliente ABC",
  "fecha_pago_limite": null,
  "id_trabajo": 1,
  "fecha_pago": "2024-01-15"
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "monto": 50000.0,
  "fecha": "2024-01-15",
  "descripcion": "Cobro de trabajo",
  "categoria": "Ingresos",
  "pagado": true,
  "forma_pago": "Transferencia",
  "metodo_pago": "Transferencia",
  "es_cobro": true,
  "destinatario": null,
  "cobrar_a": "Cliente ABC",
  "fecha_pago_limite": null,
  "id_trabajo": 1,
  "id_factura": null,
  "fecha_pago": "2024-01-15",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### PUT `/api/movimientos/{id}/update`
**Descripción**: Actualizar movimiento

**Request Body**:
```json
{
  "monto": 55000.0,
  "fecha": "2024-01-15",
  "descripcion": "Cobro de trabajo actualizado",
  "categoria": "Ingresos",
  "pagado": true,
  "forma_pago": "Efectivo",
  "es_cobro": true,
  "destinatario": null,
  "cobrar_a": "Cliente ABC",
  "fecha_pago_limite": null,
  "id_trabajo": 1,
  "fecha_pago": "2024-01-15"
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "monto": 55000.0,
  "fecha": "2024-01-15",
  "descripcion": "Cobro de trabajo actualizado",
  "categoria": "Ingresos",
  "pagado": true,
  "forma_pago": "Efectivo",
  "metodo_pago": "Efectivo",
  "es_cobro": true,
  "destinatario": null,
  "cobrar_a": "Cliente ABC",
  "fecha_pago_limite": null,
  "id_trabajo": 1,
  "id_factura": null,
  "fecha_pago": "2024-01-15",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

---

#### DELETE `/api/movimientos/{id}/delete`
**Descripción**: Eliminar movimiento

**Response 200 OK**:
```json
{
  "message": "Movimiento eliminado exitosamente"
}
```

---

### MANTENIMIENTOS

#### GET `/api/mantenimientos/`
**Descripción**: Listar todos los mantenimientos

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "id_maquina": 1,
    "fecha": "2024-01-15",
    "descripcion": "Cambio de aceite y filtros",
    "estado": "Completado",
    "costo_total": 5000.0
  }
]
```

**NOTA**: El backend debe manejar errores 500 y 404 de manera que devuelva una lista vacía `[]` en lugar de fallar, para que el frontend pueda continuar funcionando.

---

#### GET `/api/mantenimientos/{id}`
**Descripción**: Obtener mantenimiento por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "id_maquina": 1,
  "fecha": "2024-01-15",
  "descripcion": "Cambio de aceite y filtros",
  "estado": "Completado",
  "costo_total": 5000.0
}
```

---

#### POST `/api/mantenimientos/create`
**Descripción**: Crear nuevo mantenimiento

**Request Body**:
```json
{
  "id_maquina": 1,
  "fecha": "2024-01-15",
  "descripcion": "Cambio de aceite y filtros",
  "estado": "Pendiente",
  "costo_total": null
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "id_maquina": 1,
  "fecha": "2024-01-15",
  "descripcion": "Cambio de aceite y filtros",
  "estado": "Pendiente",
  "costo_total": null
}
```

---

#### PUT `/api/mantenimientos/{id}/update`
**Descripción**: Actualizar mantenimiento

**Request Body**:
```json
{
  "id_maquina": 1,
  "fecha": "2024-01-15",
  "descripcion": "Cambio de aceite y filtros completado",
  "estado": "Completado",
  "costo_total": 5000.0
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "id_maquina": 1,
  "fecha": "2024-01-15",
  "descripcion": "Cambio de aceite y filtros completado",
  "estado": "Completado",
  "costo_total": 5000.0
}
```

---

#### DELETE `/api/mantenimientos/{id}/delete`
**Descripción**: Eliminar mantenimiento

**Response 200 OK**:
```json
{
  "message": "Mantenimiento eliminado exitosamente"
}
```

---

### INSUMOS

#### GET `/api/insumos/`
**Descripción**: Listar todos los insumos

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "nombre": "Semilla de Soja",
    "categoria": "Semillas",
    "unidad": "kg",
    "stock_actual": 1000.0,
    "stock_minimo": 500.0,
    "precio_unitario": 50.0,
    "proveedor": "Proveedor ABC",
    "fecha_vencimiento": "2025-12-31",
    "observaciones": "Semilla certificada",
    "activo": true
  }
]
```

---

#### GET `/api/insumos/{id}`
**Descripción**: Obtener insumo por ID

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Semilla de Soja",
  "categoria": "Semillas",
  "unidad": "kg",
  "stock_actual": 1000.0,
  "stock_minimo": 500.0,
  "precio_unitario": 50.0,
  "proveedor": "Proveedor ABC",
  "fecha_vencimiento": "2025-12-31",
  "observaciones": "Semilla certificada",
  "activo": true
}
```

---

#### POST `/api/insumos/create`
**Descripción**: Crear nuevo insumo

**Request Body**:
```json
{
  "nombre": "Semilla de Soja",
  "categoria": "Semillas",
  "unidad": "kg",
  "stock_actual": 1000.0,
  "stock_minimo": 500.0,
  "precio_unitario": 50.0,
  "proveedor": "Proveedor ABC",
  "fecha_vencimiento": "2025-12-31",
  "observaciones": "Semilla certificada",
  "activo": true
}
```

**Response 201 Created**:
```json
{
  "id": 1,
  "nombre": "Semilla de Soja",
  "categoria": "Semillas",
  "unidad": "kg",
  "stock_actual": 1000.0,
  "stock_minimo": 500.0,
  "precio_unitario": 50.0,
  "proveedor": "Proveedor ABC",
  "fecha_vencimiento": "2025-12-31",
  "observaciones": "Semilla certificada",
  "activo": true
}
```

---

#### PUT `/api/insumos/{id}/update`
**Descripción**: Actualizar insumo

**Request Body**:
```json
{
  "nombre": "Semilla de Soja Actualizada",
  "categoria": "Semillas",
  "unidad": "kg",
  "stock_actual": 1200.0,
  "stock_minimo": 500.0,
  "precio_unitario": 55.0,
  "proveedor": "Proveedor ABC",
  "fecha_vencimiento": "2025-12-31",
  "observaciones": "Semilla certificada actualizada",
  "activo": true
}
```

**Response 200 OK**:
```json
{
  "id": 1,
  "nombre": "Semilla de Soja Actualizada",
  "categoria": "Semillas",
  "unidad": "kg",
  "stock_actual": 1200.0,
  "stock_minimo": 500.0,
  "precio_unitario": 55.0,
  "proveedor": "Proveedor ABC",
  "fecha_vencimiento": "2025-12-31",
  "observaciones": "Semilla certificada actualizada",
  "activo": true
}
```

---

#### DELETE `/api/insumos/{id}/delete`
**Descripción**: Eliminar insumo

**Response 200 OK**:
```json
{
  "message": "Insumo eliminado exitosamente"
}
```

---

## ENDPOINTS OPTIMIZADOS FLUTTER

Estos endpoints están optimizados para el frontend Flutter y devuelven datos en formato estructurado con paginación.

### GET `/api/flutter/trabajos/lista`
**Descripción**: Lista optimizada de trabajos para Flutter

**Query Parameters**:
- `skip` (int, opcional): Número de registros a saltar (default: 0)
- `limit` (int, opcional): Número máximo de registros (default: 50)
- `estado` (string, opcional): Filtrar por estado (ej: "Pendiente", "En curso", "Completado")

**Response 200 OK**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "id_tipo_trabajo": 1,
      "tipo": "Siembra",
      "cultivo": "Soja",
      "fecha_inicio": "2024-01-15",
      "fecha_fin": "2024-01-20",
      "id_personal": [1, 2],
      "id_maquinas": [1, 2],
      "campo_id": 1,
      "campo_nombre": "Campo Norte",
      "campo_ha": 50.5,
      "estado": "Completado",
      "observaciones": "Trabajo completado exitosamente",
      "a_terceros": false,
      "cobrado": true,
      "monto_cobrado": 50000.0,
      "cliente": null,
      "servicio_contratado": false
    }
  ],
  "pagination": {
    "total": 100,
    "skip": 0,
    "limit": 50,
    "has_more": true
  }
}
```

---

### GET `/api/flutter/campos/lista`
**Descripción**: Lista optimizada de campos para Flutter

**Response 200 OK**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Campo Norte",
      "hectareas": 50.5,
      "latitud": -34.603722,
      "longitud": -58.381592,
      "detalles": "Campo principal de siembra"
    }
  ],
  "pagination": {
    "total": 10,
    "skip": 0,
    "limit": 100,
    "has_more": false
  }
}
```

---

### GET `/api/flutter/maquinas/lista`
**Descripción**: Lista optimizada de máquinas para Flutter

**Response 200 OK**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Tractor John Deere",
      "marca": "John Deere",
      "modelo": "6120M",
      "ano": 2020,
      "detalles": "Tractor principal",
      "ancho_trabajo": 3.5,
      "estado": "Disponible"
    }
  ],
  "pagination": {
    "total": 5,
    "skip": 0,
    "limit": 100,
    "has_more": false
  }
}
```

---

### GET `/api/flutter/personal/lista`
**Descripción**: Lista optimizada de personal para Flutter

**Response 200 OK**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Juan Pérez",
      "dni": "12345678",
      "telefono": "+5491123456789"
    }
  ],
  "pagination": {
    "total": 20,
    "skip": 0,
    "limit": 100,
    "has_more": false
  }
}
```

---

### GET `/api/flutter/clientes/lista`
**Descripción**: Lista optimizada de clientes para Flutter

**Response 200 OK**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Agro S.A.",
      "email": "contacto@agro.com",
      "telefono": "+5491123456789",
      "direccion": "Av. Principal 123",
      "cuit": "20-12345678-9"
    }
  ],
  "pagination": {
    "total": 15,
    "skip": 0,
    "limit": 100,
    "has_more": false
  }
}
```

---

### GET `/api/flutter/costos/lista`
**Descripción**: Lista optimizada de costos para Flutter

**Query Parameters**:
- `categoria` (string, opcional): Filtrar por categoría
- `pagado` (boolean, opcional): Filtrar por estado de pago

**Response 200 OK**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "monto": 5000.0,
      "fecha": "2024-01-15",
      "destinatario": "Proveedor ABC",
      "pagado": true,
      "forma_pago": "Transferencia",
      "descripcion": "Compra de semillas",
      "categoria": "Semillas",
      "fecha_pago_limite": "2024-01-20",
      "es_cobro": false,
      "cobrar_a": null,
      "id_trabajo": null
    }
  ],
  "pagination": {
    "total": 50,
    "skip": 0,
    "limit": 100,
    "has_more": false
  }
}
```

---

### GET `/api/flutter/facturas/lista`
**Descripción**: Lista optimizada de facturas para Flutter

**Query Parameters**:
- `estado` (string, opcional): Filtrar por estado (ej: "Pendiente", "Pagada", "Vencida")

**Response 200 OK**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "cliente_id": 1,
      "numero": "FAC-001",
      "fecha_emision": "2024-01-15",
      "fecha_vencimiento": "2024-02-15",
      "monto_total": 100000.0,
      "monto_pagado": 50000.0,
      "estado": "Pendiente"
    }
  ],
  "pagination": {
    "total": 25,
    "skip": 0,
    "limit": 100,
    "has_more": false
  }
}
```

---

### GET `/api/flutter/dashboard/resumen`
**Descripción**: Resumen del dashboard optimizado para Flutter

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "trabajos_pendientes": 5,
    "trabajos_en_curso": 3,
    "trabajos_completados": 20,
    "ingresos_mes": 500000.0,
    "gastos_mes": 300000.0,
    "balance_mes": 200000.0,
    "facturas_pendientes": 10,
    "facturas_vencidas": 2,
    "mantenimientos_pendientes": 3,
    "insumos_bajo_stock": 5
  }
}
```

---

## ENDPOINTS DE DASHBOARD Y REPORTES

### GET `/api/dashboard/resumen`
**Descripción**: Resumen general del dashboard

**Response 200 OK**:
```json
{
  "trabajos_pendientes": 5,
  "trabajos_en_curso": 3,
  "trabajos_completados": 20,
  "ingresos_mes": 500000.0,
  "gastos_mes": 300000.0,
  "balance_mes": 200000.0,
  "facturas_pendientes": 10,
  "facturas_vencidas": 2,
  "mantenimientos_pendientes": 3,
  "insumos_bajo_stock": 5
}
```

---

### GET `/api/dashboard/estadisticas`
**Descripción**: Estadísticas generales del sistema

**Response 200 OK**:
```json
{
  "total_trabajos": 28,
  "total_campos": 10,
  "total_maquinas": 5,
  "total_personal": 20,
  "total_clientes": 15,
  "superficie_total_ha": 500.5,
  "ingresos_totales": 2000000.0,
  "gastos_totales": 1200000.0,
  "balance_total": 800000.0
}
```

---

### GET `/api/reportes/trabajos`
**Descripción**: Reporte de trabajos

**Response 200 OK**:
```json
{
  "periodo": "2024-01",
  "total_trabajos": 20,
  "trabajos_por_tipo": {
    "Siembra": 10,
    "Cosecha": 5,
    "Laboreo": 5
  },
  "trabajos_por_estado": {
    "Pendiente": 5,
    "En curso": 3,
    "Completado": 12
  },
  "superficie_total_ha": 500.5,
  "ingresos_totales": 1000000.0
}
```

---

### GET `/api/reportes/financiero`
**Descripción**: Reporte financiero

**Response 200 OK**:
```json
{
  "periodo": "2024-01",
  "ingresos": {
    "total": 500000.0,
    "por_categoria": {
      "Trabajos": 400000.0,
      "Otros": 100000.0
    }
  },
  "gastos": {
    "total": 300000.0,
    "por_categoria": {
      "Semillas": 100000.0,
      "Fertilizantes": 80000.0,
      "Combustible": 50000.0,
      "Mano de obra": 70000.0
    }
  },
  "balance": 200000.0,
  "facturas_pendientes": 10,
  "facturas_vencidas": 2
}
```

---

## ENDPOINTS MÓVILES

### GET `/api/mobile/sync`
**Descripción**: Sincronización de datos para aplicación móvil

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "trabajos": [...],
    "campos": [...],
    "maquinas": [...],
    "personal": [...],
    "clientes": [...],
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

### POST `/api/mobile/sync`
**Descripción**: Enviar datos desde aplicación móvil

**Request Body**:
```json
{
  "trabajos": [...],
  "movimientos": [...],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response 200 OK**:
```json
{
  "success": true,
  "message": "Datos sincronizados exitosamente",
  "sincronizados": {
    "trabajos": 5,
    "movimientos": 10
  }
}
```

---

## CÓDIGOS DE ERROR ESTÁNDAR

### 200 OK
Operación exitosa

### 201 Created
Recurso creado exitosamente

### 400 Bad Request
Error en los datos enviados
```json
{
  "detail": "Descripción del error"
}
```

### 401 Unauthorized
Token inválido o expirado
```json
{
  "detail": "Token inválido o expirado"
}
```

### 403 Forbidden
No tiene permisos para realizar la operación
```json
{
  "detail": "No tiene permisos para realizar esta operación"
}
```

### 404 Not Found
Recurso no encontrado
```json
{
  "detail": "Recurso no encontrado"
}
```

### 500 Internal Server Error
Error interno del servidor
```json
{
  "detail": "Error interno del servidor"
}
```

---

## NOTAS IMPORTANTES PARA EL BACKEND

### 1. Autenticación
- Todos los endpoints (excepto `/api/auth/*` y `/api/health/`) requieren autenticación Bearer Token
- El token se envía en el header `Authorization: Bearer {token}`
- El backend debe validar el token en cada request

### 2. Formato de Fechas
- **Siempre usar formato**: `YYYY-MM-DD` para fechas simples
- **Para fechas con hora**: `YYYY-MM-DDTHH:mm:ssZ` (ISO8601)

### 3. Campos Booleanos
- El frontend puede enviar booleanos como `true/false`, `1/0`, o `"true"/"false"`
- El backend debe aceptar todos estos formatos y normalizarlos

### 4. Arrays en Trabajos
- `id_personal` y `id_maquinas` son arrays de enteros: `[1, 2, 3]`
- El backend debe validar que estos IDs existan

### 5. Personal con Hectáreas
- Cuando se crea/actualiza un trabajo, el frontend puede enviar `personal_hectareas` como array de objetos:
  ```json
  [
    {"id": 1, "ha": 25.5},
    {"id": 2, "ha": 25.0}
  ]
  ```
- Este campo es OPCIONAL pero RECOMENDADO para mantener la consistencia

### 6. Campo "tipo" en Trabajos
- El backend DEBE devolver el nombre del tipo de trabajo en el campo `tipo` además del `id_tipo_trabajo`
- Ejemplo: `{"id_tipo_trabajo": 1, "tipo": "Siembra"}`

### 7. Manejo de Errores
- Para `/api/mantenimientos/`, si hay un error 500 o 404, devolver lista vacía `[]` en lugar de fallar
- Esto permite que el frontend continúe funcionando

### 8. Paginación
- Los endpoints de lista deben soportar `skip` y `limit` como query parameters
- Los endpoints optimizados Flutter deben devolver estructura con `pagination`

### 9. Validación de DNI
- El endpoint `/api/personal/validate-dni` debe verificar que el DNI no esté duplicado
- Si se proporciona `exclude_id`, excluir ese ID de la validación (útil para actualizaciones)

### 10. Campos de Cosecha
- Si `id_tipo_trabajo == 1` (Cosecha), los campos `rinde_cosecha` y `humedad_cosecha` pueden tener valores reales
- Si `id_tipo_trabajo != 1`, estos campos deben ser `0.0`

---

## ESTRUCTURA DE BASE DE DATOS SUGERIDA

### Tablas Principales
- `usuarios`
- `campos`
- `clientes`
- `campos_cliente` (tabla de relación)
- `maquinas`
- `personal`
- `tipo_trabajo`
- `trabajos`
- `trabajo_personal` (tabla de relación con hectáreas)
- `trabajo_maquinas` (tabla de relación)
- `costos`
- `facturas`
- `factura_items`
- `creditos`
- `cuotas_credito`
- `pagos`
- `movimientos`
- `mantenimientos`
- `insumos`

---

## CONCLUSIÓN

Este documento contiene TODA la especificación necesaria para que el backend funcione correctamente con el frontend Flutter. Cada endpoint está documentado con:
- Método HTTP
- Ruta completa
- Parámetros de query (si aplica)
- Formato de request body
- Formato de response
- Códigos de error posibles

**IMPORTANTE**: El backend debe implementar TODOS estos endpoints exactamente como se especifica aquí para garantizar la compatibilidad completa con el frontend.

