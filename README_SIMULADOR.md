# 🤖 Simulador de WhatsApp CLI - Inicio Rápido

## ✨ ¿Qué es esto?

Un simulador que te permite **depurar tu webhook de WhatsApp localmente** sin necesidad de Twilio real. La consola actúa como Twilio, interceptando las respuestas y mostrándolas en pantalla.

## 🚀 Uso Rápido

### Opción 1: Simulador Interactivo (Recomendado)

```bash
python test_whatsapp_cli.py
```

**Características:**
- ✅ Sesión interactiva tipo chat
- ✅ Mockea Twilio completamente
- ✅ Ejecuta el webhook real con OpenAI y tools
- ✅ Muestra las respuestas que se enviarían a WhatsApp
- ✅ Colores y formato amigable

**Flujo:**
```
Tú escribes → Webhook procesa → OpenAI responde → Tools ejecutan → Consola muestra
```

### Opción 2: Mensaje Único

```bash
python send_whatsapp_message.py "Listar mis campos"
```

**Características:**
- ✅ Envía un solo mensaje
- ✅ Útil para scripts o pruebas rápidas
- ✅ Puede especificar teléfono con `--phone`

### Opción 3: Modo Debug (Sin Twilio)

```bash
python test_whatsapp_debug.py
```

**Características:**
- ✅ Llama directamente al controlador
- ✅ No pasa por el webhook completo
- ✅ Útil para depurar solo la lógica de OpenAI

## 📋 Requisitos

1. **Usuario con teléfono**: Necesitas al menos un usuario con el campo `telefono` configurado.

2. **OpenAI configurado**: Variable `OPENAI_API_KEY` en tu `.env`

3. **Django funcionando**: El simulador usa Django directamente

## 💡 Ejemplos de Mensajes

Una vez en el simulador interactivo, prueba:

```
> Hola, qué puedes hacer?
> Listar mis campos
> Mostrar todas las máquinas
> Crear un nuevo campo llamado La Esperanza de 100 hectáreas
> Cuántas horas trabajó la máquina 123 esta semana?
> Mostrar el reporte de hoy
```

## 🔧 Cómo Funciona

El simulador **mockea (simula) el cliente de Twilio**:

1. Creas un mensaje en la consola
2. El simulador lo envía al webhook (como lo haría Twilio)
3. El webhook procesa normalmente (valida, llama OpenAI, ejecuta tools)
4. Cuando el webhook intenta enviar la respuesta por Twilio...
5. **El mock intercepta la llamada** y la muestra en consola
6. Ves exactamente lo que se enviaría a WhatsApp

**Ventaja:** Ejecutas el código real sin modificarlo, pero sin enviar mensajes reales.

## 🎯 Casos de Uso

### Depurar Tools de OpenAI

```bash
python test_whatsapp_cli.py
> Crear un campo llamado Test de 50 hectáreas
```

Verás:
- La llamada a OpenAI
- La ejecución del tool `crear_campo`
- La respuesta generada
- Todo en tiempo real

### Probar Flujo Completo

```bash
python test_whatsapp_cli.py
> Listar campos
> Crear campo Nuevo de 100 ha
> Listar campos
```

Verás cómo el agente mantiene contexto y ejecuta múltiples operaciones.

### Prueba Rápida

```bash
python send_whatsapp_message.py "Mostrar mis máquinas" --verbose
```

## 📚 Documentación Completa

Para más detalles, ver:
- **`WHATSAPP_CLI_SIMULATOR.md`**: Documentación completa con troubleshooting
- **`WHATSAPP_SETUP.md`**: Configuración de Twilio real para producción

## 🆘 Problemas Comunes

### "No hay usuarios con teléfono"

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
user.telefono = '+5491112345678'  # Tu número
user.save()
```

### "No estás autorizado"

El sistema valida que el teléfono esté en la base de datos. Asegúrate de que el usuario tenga el campo `telefono` configurado.

### Errores de OpenAI

Verifica que `OPENAI_API_KEY` esté en tu `.env` y que tengas créditos.

## 🎨 Comandos en el Simulador

Dentro del simulador interactivo:

- **`help`**: Muestra ayuda
- **`clear`** o **`cls`**: Limpia pantalla
- **`salir`** o **`exit`**: Cierra el simulador

## 🔍 Ver Logs Detallados

Los logs del webhook aparecen en la consola. Verás:

```
INFO whatsapp_api 📱 MENSAJE DE WHATSAPP RECIBIDO
INFO whatsapp_controller 🚀 INICIANDO PROCESAMIENTO
INFO whatsapp_openai_agent 🤖 Llamando a OpenAI...
INFO whatsapp_openai_agent 🔧 Ejecutando tool: listar_campos
INFO whatsapp_api ✅ Respuesta enviada exitosamente
```

## 🎉 ¡Listo!

Ahora puedes depurar tu webhook de WhatsApp localmente sin necesidad de Twilio real. La consola simula todo el flujo de Twilio, permitiéndote ver exactamente qué se enviaría a los usuarios.

**Disfruta depurando! 🚀**
