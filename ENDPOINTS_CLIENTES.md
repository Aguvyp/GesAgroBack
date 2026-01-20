# 📋 Documentación de Endpoints - Entidad Clientes

## 🔧 Atributos de la Entidad Cliente

La entidad `Cliente` tiene los siguientes atributos:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del cliente (auto-generado) |
| `nombre` | String (255) | No | Nombre del cliente |
| `email` | Email | No | Correo electrónico del cliente |
| `telefono` | String (50) | No | Teléfono del cliente |
| `direccion` | String (500) | No | Dirección del cliente |
| `cuit` | String (20) | No | CUIT del cliente |
| `observaciones` | Text | No | Observaciones adicionales |
| `fecha_creacion` | DateTime | Auto | Fecha de creación (auto-generado) |
| `fecha_modificacion` | DateTime | Auto | Fecha de última modificación (auto-actualizado) |
| `usuario_id` | Integer | Auto | ID del usuario propietario (auto-asignado desde token) |
| `created_at` | DateTime | Auto | Timestamp de creación (auto-generado) |
| `updated_at` | DateTime | Auto | Timestamp de actualización (auto-actualizado) |

---

## 📡 Endpoints Disponibles

### 1. **LISTAR TODOS LOS CLIENTES** (LIST)

**Método:** `GET`  
**URL:** `/api/clientes/`  
**Autenticación:** Requerida (Bearer Token)

**Headers:**
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Payload:** No requiere body

**Respuesta Exitosa (200):**
```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan.perez@example.com",
    "telefono": "3512345678",
    "direccion": "Av. Colón 1234, Córdoba",
    "cuit": "20-12345678-9",
    "observaciones": "Cliente preferencial",
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_modificacion": "2024-01-20T14:45:00Z",
    "usuario_id": 5,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z"
  },
  {
    "id": 2,
    "nombre": "María González",
    "email": "maria.gonzalez@example.com",
    "telefono": "3519876543",
    "direccion": "Calle Falsa 123, Córdoba",
    "cuit": "27-98765432-1",
    "observaciones": null,
    "fecha_creacion": "2024-02-01T08:00:00Z",
    "fecha_modificacion": "2024-02-01T08:00:00Z",
    "usuario_id": 5,
    "created_at": "2024-02-01T08:00:00Z",
    "updated_at": "2024-02-01T08:00:00Z"
  }
]
```

---

### 2. **OBTENER UN CLIENTE ESPECÍFICO** (DETAIL)

**Método:** `GET`  
**URL:** `/api/clientes/<id>/`  
**Autenticación:** Requerida (Bearer Token)

**Headers:**
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Parámetros URL:**
- `id`: ID del cliente a obtener

**Payload:** No requiere body

**Respuesta Exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "telefono": "3512345678",
  "direccion": "Av. Colón 1234, Córdoba",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente preferencial",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_modificacion": "2024-01-20T14:45:00Z",
  "usuario_id": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

**Respuesta Error (404):**
```json
{
  "detail": "Not found."
}
```

---

### 3. **CREAR CLIENTE** (CREATE/ALTA)

**Método:** `POST`  
**URL:** `/api/clientes/create/`  
**Autenticación:** Requerida (Bearer Token)

**Headers:**
```json
{
  "Authorization": "Bearer <access_token>",
  "Content-Type": "application/json"
}
```

**Payload (Body):**
```json
{
  "nombre": "Carlos Rodríguez",
  "email": "carlos.rodriguez@example.com",
  "telefono": "3514567890",
  "direccion": "Bv. San Juan 456, Córdoba",
  "cuit": "20-45678901-2",
  "observaciones": "Nuevo cliente - contacto por referencia"
}
```

**Campos Mínimos Requeridos:**
Todos los campos son opcionales, pero se recomienda al menos enviar `nombre`.

**Respuesta Exitosa (201):**
```json
{
  "id": 3,
  "nombre": "Carlos Rodríguez",
  "email": "carlos.rodriguez@example.com",
  "telefono": "3514567890",
  "direccion": "Bv. San Juan 456, Córdoba",
  "cuit": "20-45678901-2",
  "observaciones": "Nuevo cliente - contacto por referencia",
  "fecha_creacion": "2024-03-10T12:00:00Z",
  "fecha_modificacion": "2024-03-10T12:00:00Z",
  "usuario_id": 5,
  "created_at": "2024-03-10T12:00:00Z",
  "updated_at": "2024-03-10T12:00:00Z"
}
```

**Notas:**
- El campo `usuario_id` se asigna automáticamente desde el token de autenticación
- Los campos `fecha_creacion`, `fecha_modificacion`, `created_at` y `updated_at` se generan automáticamente

---

### 4. **ACTUALIZAR CLIENTE** (UPDATE/MODIFICACIÓN)

**Método:** `PUT` o `PATCH`  
**URL:** `/api/clientes/<id>/update/`  
**Autenticación:** Requerida (Bearer Token)

**Headers:**
```json
{
  "Authorization": "Bearer <access_token>",
  "Content-Type": "application/json"
}
```

**Parámetros URL:**
- `id`: ID del cliente a actualizar

**Payload (Body) - PUT (todos los campos):**
```json
{
  "nombre": "Juan Pérez Actualizado",
  "email": "juan.perez.nuevo@example.com",
  "telefono": "3512345679",
  "direccion": "Av. Colón 1234 - Piso 2, Córdoba",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente preferencial - Actualizado datos de contacto"
}
```

**Payload (Body) - PATCH (solo campos a modificar):**
```json
{
  "telefono": "3512345679",
  "observaciones": "Actualizado teléfono de contacto"
}
```

**Respuesta Exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez Actualizado",
  "email": "juan.perez.nuevo@example.com",
  "telefono": "3512345679",
  "direccion": "Av. Colón 1234 - Piso 2, Córdoba",
  "cuit": "20-12345678-9",
  "observaciones": "Cliente preferencial - Actualizado datos de contacto",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_modificacion": "2024-03-10T15:30:00Z",
  "usuario_id": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-03-10T15:30:00Z"
}
```

**Respuesta Error (404):**
```json
{
  "detail": "Not found."
}
```

**Notas:**
- Solo se pueden actualizar clientes del usuario autenticado
- El campo `fecha_modificacion` y `updated_at` se actualizan automáticamente

---

### 5. **ELIMINAR CLIENTE** (DELETE/BAJA)

**Método:** `DELETE`  
**URL:** `/api/clientes/<id>/delete/`  
**Autenticación:** Requerida (Bearer Token)

**Headers:**
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Parámetros URL:**
- `id`: ID del cliente a eliminar

**Payload:** No requiere body

**Respuesta Exitosa (204):**
```
No Content
```

**Respuesta Error (404):**
```json
{
  "detail": "Not found."
}
```

**Notas:**
- Solo se pueden eliminar clientes del usuario autenticado
- La eliminación es permanente (hard delete)

---

## 🔐 Autenticación

Todos los endpoints requieren autenticación mediante Bearer Token:

```
Authorization: Bearer <access_token>
```

El token se obtiene del endpoint de login: `/api/auth/login/`

---

## 📝 Notas para el Frontend

### Campos Auto-gestionados (No enviar en formularios):
- `id`
- `usuario_id`
- `fecha_creacion`
- `fecha_modificacion`
- `created_at`
- `updated_at`

### Campos Editables por el Usuario:
- `nombre` ✏️
- `email` ✏️
- `telefono` ✏️
- `direccion` ✏️
- `cuit` ✏️
- `observaciones` ✏️

### Validaciones Recomendadas en Frontend:
- **email**: Validar formato de email
- **cuit**: Validar formato de CUIT argentino (XX-XXXXXXXX-X)
- **telefono**: Validar formato de teléfono
- **nombre**: Máximo 255 caracteres
- **telefono**: Máximo 50 caracteres
- **direccion**: Máximo 500 caracteres
- **cuit**: Máximo 20 caracteres

### Ejemplo de Interfaz TypeScript:

```typescript
interface Cliente {
  id: number;
  nombre: string | null;
  email: string | null;
  telefono: string | null;
  direccion: string | null;
  cuit: string | null;
  observaciones: string | null;
  fecha_creacion: string;
  fecha_modificacion: string;
  usuario_id: number | null;
  created_at: string;
  updated_at: string;
}

interface ClienteForm {
  nombre?: string;
  email?: string;
  telefono?: string;
  direccion?: string;
  cuit?: string;
  observaciones?: string;
}
```

---

## 📊 Resumen de Endpoints

| Operación | Método | URL | Descripción |
|-----------|--------|-----|-------------|
| **LIST** | GET | `/api/clientes/` | Listar todos los clientes |
| **DETAIL** | GET | `/api/clientes/<id>/` | Obtener un cliente específico |
| **CREATE** | POST | `/api/clientes/create/` | Crear un nuevo cliente |
| **UPDATE** | PUT/PATCH | `/api/clientes/<id>/update/` | Actualizar un cliente |
| **DELETE** | DELETE | `/api/clientes/<id>/delete/` | Eliminar un cliente |

---

**Última actualización:** 2026-01-20
