# ✅ SIMULADOR DE WHATSAPP CLI - FUNCIONANDO

## 🎉 Resumen

He creado exitosamente un **simulador de WhatsApp CLI** que te permite depurar tu webhook localmente sin necesidad de Twilio real.

## 📁 Archivos Creados

### 1. **`test_whatsapp_cli.py`** ⭐ (Principal - USAR ESTE)
Script interactivo que simula completamente Twilio. 

**Características:**
- ✅ Chat interactivo en consola
- ✅ Mockea Twilio completamente (intercepta las llamadas)
- ✅ Ejecuta el webhook real con todos sus pasos
- ✅ Procesa con OpenAI y ejecuta tools
- ✅ Muestra las respuestas en consola
- ✅ Se mantiene abierto hasta que presiones Ctrl+C o escribas "salir"

**Uso:**
```bash
python test_whatsapp_cli.py
```

### 2. **`test_whatsapp_debug.py`**
Versión simplificada que llama directamente al controlador sin pasar por el webhook.

**Uso:**
```bash
python test_whatsapp_debug.py
```

### 3. **`send_whatsapp_message.py`**
Script para enviar un solo mensaje (útil para pruebas rápidas o scripts).

**Uso:**
```bash
python send_whatsapp_message.py "Listar mis campos"
python send_whatsapp_message.py "Hola" --phone +5491112345678 --verbose
```

### 4. **Documentación**
- `README_SIMULADOR.md`: Guía rápida de inicio
- `WHATSAPP_CLI_SIMULATOR.md`: Documentación completa con troubleshooting

## 🚀 Cómo Usar (Inicio Rápido)

### Paso 1: Ejecutar el Simulador

```bash
python test_whatsapp_cli.py
```

### Paso 2: Escribir Mensajes

El simulador te mostrará un prompt:

```
📱 Tú >
```

Escribe cualquier mensaje y presiona Enter.

### Paso 3: Ver las Respuestas

El simulador mostrará:
1. Tu mensaje (como si fuera recibido por Twilio)
2. El procesamiento del webhook
3. La respuesta del asistente (como si fuera enviada por Twilio)

### Paso 4: Salir

Escribe `salir` o presiona `Ctrl+C`

## ✨ Ejemplo de Sesión

```
📱 Tú > Hola, qué puedes hacer?

[22:28:07] 📱 WhatsApp → Webhook
👤 Usuario: Hola, qué puedes hacer?

[22:28:07] ⚙️  Sistema: Procesando en webhook... (validando, llamando OpenAI, ejecutando tools...)

[22:28:13] 📤 Webhook → Twilio → WhatsApp
🤖 Asistente: ¡Hola! Puedo ayudarte a gestionar una empresa agrícola mediante las siguientes funciones:

1. **Trabajos agrícolas**: Crear, actualizar o eliminar trabajos como siembra, cosecha, pulverización, etc.
2. **Costos y gastos**: Registrar y actualizar costos relacionados con la actividad agrícola.
3. **Campos**: Crear, actualizar y eliminar registros de campos agrícolas.
4. **Clientes**: Gestionar información de clientes, incluyendo la creación, actualización y eliminación de registros.

Si necesitas realizar alguna acción específica, no dudes en decírmelo.
   [Message SID: SM20260120222813598686]

📱 Tú > Listar mis campos

[22:28:24] 📱 WhatsApp → Webhook
👤 Usuario: Listar mis campos

[22:28:24] ⚙️  Sistema: Procesando en webhook... (validando, llamando OpenAI, ejecutando tools...)

[22:28:32] 📤 Webhook → Twilio → WhatsApp
🤖 Asistente: Tus campos son los siguientes:

1. **Nombre:** Tononio
   - **Hectáreas:** 250.00

2. **Nombre:** Stangaferro
   - **Hectáreas:** 180.00

3. **Nombre:** Carolina
   - **Hectáreas:** 120.00

Si necesitas más información o realizar alguna acción, házmelo saber.
   [Message SID: SM20260120222832214429]

📱 Tú > salir

👋 Cerrando sesión...
Total de mensajes enviados: 2
```

## 🔧 Cómo Funciona

### El Flujo Completo

```
1. Escribes mensaje en consola
   ↓
2. Script simula request POST de Twilio → Webhook
   ↓
3. Webhook valida autorización del teléfono
   ↓
4. Webhook procesa con OpenAI
   ↓
5. OpenAI decide qué tools ejecutar
   ↓
6. Tools se ejecutan (listar_campos, crear_campo, etc.)
   ↓
7. OpenAI genera respuesta con los resultados
   ↓
8. Webhook intenta enviar respuesta por Twilio
   ↓
9. Mock intercepta la llamada a Twilio
   ↓
10. Consola muestra la respuesta
```

### El Mockeo de Twilio

El simulador usa **mocking de Python** para interceptar las llamadas a Twilio:

```python
# Cuando el webhook hace esto:
client = Client(account_sid, auth_token)
message = client.messages.create(
    body="Respuesta del asistente",
    from_='whatsapp:+14155238886',
    to='whatsapp:+5493498416451'
)

# El mock intercepta y en lugar de enviar el mensaje real:
# - Captura el body
# - Lo muestra en consola
# - Retorna un objeto simulado
```

## 💡 Ventajas

1. ✅ **Flujo completo**: Ejecuta TODO el código real (webhook, OpenAI, tools)
2. ✅ **Sin modificar código**: No necesitas cambiar nada en tu webhook
3. ✅ **Depuración realista**: Ves exactamente cómo funcionaría en producción
4. ✅ **Sin costos de Twilio**: No consume créditos de Twilio (pero sí de OpenAI)
5. ✅ **Rápido**: No hay latencia de red con Twilio
6. ✅ **Interactivo**: Puedes mantener conversaciones completas
7. ✅ **Logs detallados**: Ves todos los logs del procesamiento

## 🎯 Casos de Uso

### 1. Depurar Tools de OpenAI

```bash
python test_whatsapp_cli.py
> Crear un campo llamado Test de 50 hectáreas
```

Verás:
- La llamada a OpenAI
- La decisión de usar el tool `crear_campo`
- La ejecución del tool
- La respuesta generada

### 2. Probar Flujo Completo

```bash
python test_whatsapp_cli.py
> Listar campos
> Crear campo Nuevo de 100 ha
> Listar campos
```

Verás cómo el agente mantiene contexto y ejecuta múltiples operaciones.

### 3. Depurar Errores

Si algo falla, verás:
- Logs detallados en la consola
- El error exacto
- El stack trace completo

## 📝 Comandos Disponibles

Dentro del simulador:

- **`help`**: Muestra ayuda con ejemplos
- **`clear`** o **`cls`**: Limpia la pantalla
- **`salir`** o **`exit`**: Cierra el simulador

## 🔍 Ver Logs Detallados

Los logs del webhook aparecen en la consola mientras el simulador corre:

```
INFO whatsapp_api 📱 MENSAJE DE WHATSAPP RECIBIDO
INFO whatsapp_controller 🚀 INICIANDO PROCESAMIENTO
INFO whatsapp_controller 📋 PASO 1: Validando autorización...
INFO whatsapp_controller ✅ Teléfono autorizado
INFO whatsapp_controller 📋 PASO 2: Obteniendo texto del mensaje...
INFO whatsapp_controller 📋 PASO 3: Procesando con OpenAI...
INFO whatsapp_openai_agent 🤖 Enviando mensaje a OpenAI...
INFO whatsapp_openai_agent 📞 Llamando función: get_campos
INFO whatsapp_openai_agent 🔧 Ejecutando función: get_campos
INFO whatsapp_openai_agent ✅ Respuesta de OpenAI
INFO whatsapp_api ✅ Respuesta enviada exitosamente
```

## 🎉 ¡Listo para Usar!

El simulador está **100% funcional** y probado. Puedes:

1. Ejecutar `python test_whatsapp_cli.py`
2. Escribir mensajes como si estuvieras en WhatsApp
3. Ver las respuestas del agente en tiempo real
4. Depurar el flujo completo sin necesidad de Twilio real
5. Mantener la conversación abierta hasta que presiones Ctrl+C

**¡Disfruta depurando! 🚀**
