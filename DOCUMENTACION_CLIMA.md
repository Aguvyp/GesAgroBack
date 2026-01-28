# API de Clima (Open-Meteo Wrapper)

Este endpoint actúa como un wrapper optimizado para la API de Open-Meteo, proporcionando información meteorológica actual y pronóstico para los próximos 5 días, adaptado para las necesidades de gestión agrícola.

## Endpoint

**URL:** `/api/clima/pronostico/`  
**Método:** `GET`  
**Autenticación:** Requerida (Bearer Token)

## Parámetros de Consulta (Query Params)

| Parámetro | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `lat` | Float | Sí | Latitud de la ubicación. |
| `lon` | Float | Sí | Longitud de la ubicación. |

## Lógica de Negocio

- **Procesamiento de Clima:** Los códigos WMO se transforman en descripciones legibles en español.
- **Alerta de Pulverización:** Se activa (`true`) si la velocidad del viento actual es superior a **15 km/h**.
- **Sistema de Cache:** 
    - Las respuestas se almacenan por **15 minutos**.
    - La clave de cache utiliza coordenadas redondeadas a **2 decimales** para optimizar peticiones en áreas cercanas.
- **Pronóstico:** Limitado estrictamente a los próximos 5 días.

## Ejemplo de Petición

`GET /api/clima/pronostico/?lat=-34.6037&lon=-58.3816`

## Estructura de Respuesta (JSON)

### Exitosa (200 OK)

```json
{
  "actual": {
    "temperatura": 25.4,
    "humedad": 60,
    "viento": 12.5,
    "descripcion": "Parcialmente nublado",
    "alerta_pulverizacion": false
  },
  "pronostico": [
    {
      "dia": "2026-01-28",
      "dia_nombre": "Miércoles",
      "max": 30.1,
      "min": 20.5,
      "clima": "Soleado"
    },
    {
      "dia": "2026-01-29",
      "dia_nombre": "Jueves",
      "max": 28.5,
      "min": 19.2,
      "clima": "Lluvia ligera"
    },
    {
      "dia": "2026-01-30",
      "dia_nombre": "Viernes",
      "max": 27.0,
      "min": 18.5,
      "clima": "Nublado"
    },
    {
      "dia": "2026-01-31",
      "dia_nombre": "Sábado",
      "max": 29.3,
      "min": 21.0,
      "clima": "Despejado"
    },
    {
      "dia": "2026-02-01",
      "dia_nombre": "Domingo",
      "max": 31.5,
      "min": 22.1,
      "clima": "Despejado"
    }
  ]
}
```

### Error de Parámetros (400 Bad Request)

```json
{
  "error": "Se requieren los parámetros lat y lon."
}
```

### Error del Servidor/API Externa (500 Internal Server Error)

```json
{
  "error": "Error al conectar con Open-Meteo: [Detalle del error]"
}
```
