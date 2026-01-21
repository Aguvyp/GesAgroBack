# Simulador de WhatsApp CLI - Guía de Uso

Este documento explica cómo usar el simulador de WhatsApp CLI para depurar el webhook localmente.

## 🎯 Propósito

El simulador permite:
- ✅ **Simular Twilio completamente**: La consola actúa como Twilio, recibiendo y "enviando" mensajes
- ✅ **Depurar el flujo completo**: Ejecuta el webhook real con todos sus pasos (validación, OpenAI, tools)
- ✅ **Mockear las respuestas**: Intercepta las llamadas a Twilio y muestra las respuestas en consola
- ✅ **Ver el flujo real**: Exactamente como funciona en producción, pero sin enviar mensajes reales
- ✅ **Probar las herramientas (tools)**: Todas las funciones de OpenAI se ejecutan normalmente

## 📋 Requisitos Previos

1. **Usuario con teléfono configurado**: Debes tener al menos un usuario en la base de datos con un número de teléfono configurado en el campo `telefono`.

2. **Servidor Django corriendo**: El simulador llama directamente a las funciones de Django, por lo que necesitas tener el entorno configurado.

3. **Variables de entorno**: Asegúrate de tener configuradas las variables de OpenAI en tu `.env`:
   ```
   OPENAI_API_KEY=tu_api_key_aqui
   ```

## 🚀 Uso Básico

### Opción 1: Script Interactivo (Recomendado)

```bash
python test_whatsapp_cli.py
```

Este script:
1. Te muestra los usuarios disponibles con teléfono
2. Te permite seleccionar uno (o usa el único disponible automáticamente)
3. Inicia una sesión interactiva donde puedes escribir mensajes
4. Muestra las respuestas del asistente en tiempo real

### Comandos Especiales

Dentro de la sesión interactiva:

- **`salir`** o **`exit`**: Termina la sesión
- **`clear`** o **`cls`**: Limpia la pantalla
- **`help`**: Muestra ayuda con ejemplos

## 🔧 Cómo Funciona el Mockeo

El simulador utiliza **mocking** de Python para interceptar las llamadas a Twilio:

1. **Cuando escribes un mensaje**: El simulador crea una petición HTTP POST simulada, exactamente como la que enviaría Twilio al webhook.

2. **El webhook se ejecuta normalmente**: 
   - Valida el teléfono
   - Procesa el mensaje con OpenAI
   - Ejecuta las herramientas (tools) necesarias
   - Intenta enviar la respuesta por Twilio

3. **Interceptación de Twilio**: Cuando el webhook intenta crear un cliente de Twilio y enviar un mensaje:
   ```python
   client = Client(account_sid, auth_token)  # ← Esto se mockea
   message = client.messages.create(...)      # ← Esto también
   ```
   El simulador intercepta estas llamadas y en lugar de enviar el mensaje real, lo captura y lo muestra en la consola.

4. **Resultado**: Ves exactamente lo que se enviaría a WhatsApp, sin enviar mensajes reales.

### Ventajas de este Enfoque

- ✅ **Flujo completo**: Ejecuta TODO el código real, incluyendo validaciones y lógica de negocio
- ✅ **Sin modificar código**: No necesitas cambiar nada en tu webhook para depurar
- ✅ **Depuración realista**: Ves exactamente cómo funcionaría en producción
- ✅ **Sin costos**: No consume créditos de Twilio (pero sí de OpenAI)
- ✅ **Rápido**: No hay latencia de red con Twilio

## 💡 Ejemplos de Mensajes

Una vez en la sesión interactiva, puedes probar:

### Consultas Generales
```
> Hola, ¿qué puedes hacer?
> Ayúdame con mis campos
```

### Listar Datos
```
> Listar mis campos
> Mostrar todas las máquinas
> Cuáles son mis lotes?
```

### Crear Datos
```
> Crear un nuevo campo llamado "La Esperanza" de 100 hectáreas
> Agregar una máquina John Deere 6125R
```

### Consultas de Reportes
```
> Mostrar el reporte de hoy
> Cuántas horas trabajó la máquina 123 esta semana?
> Resumen de combustible del mes
```

### Actualizar Datos
```
> Cambiar el nombre del campo 5 a "San Jorge"
> Actualizar las hectáreas del lote 10 a 50
```

## 🔍 Depuración

### Ver Logs Detallados

El simulador muestra logs en la consola con colores:
- 🔵 **Azul**: Mensajes del usuario
- 🟢 **Verde**: Respuestas del asistente
- 🟡 **Amarillo**: Mensajes del sistema
- 🔴 **Rojo**: Errores

### Logs del Servidor

Para ver logs más detallados del procesamiento, revisa la consola donde corre Django. Allí verás:
- Validación de autorización
- Procesamiento con OpenAI
- Llamadas a tools/funciones
- Respuestas generadas

## 🛠️ Solución de Problemas

### "No hay usuarios con teléfono configurado"

**Solución**: Agrega un teléfono a un usuario existente:

```python
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Obtener un usuario
user = User.objects.first()

# Configurar teléfono (formato internacional)
user.telefono = '+5491112345678'  # Reemplaza con un número real
user.save()

print(f"Teléfono configurado para {user.email}: {user.telefono}")
```

### "No estás autorizado para usar este servicio"

**Solución**: El sistema valida que el teléfono esté autorizado. Verifica que:
1. El usuario tenga el campo `telefono` configurado
2. El número esté en formato internacional (+54...)
3. El servicio `whatsapp_auth` reconozca el número

### Errores de OpenAI

Si ves errores relacionados con OpenAI:
1. Verifica que `OPENAI_API_KEY` esté configurada en `.env`
2. Verifica que tengas créditos en tu cuenta de OpenAI
3. Revisa los logs para ver el error específico

## 📊 Flujo de Procesamiento

El simulador sigue este flujo:

```
1. Usuario escribe mensaje en CLI
   ↓
2. Script simula request de Twilio → Webhook
   ↓
3. Webhook valida autorización del teléfono
   ↓
4. Webhook procesa con OpenAI (puede llamar tools)
   ↓
5. Webhook intenta enviar respuesta por Twilio
   ↓
6. Mock intercepta la llamada a Twilio
   ↓
7. CLI muestra la respuesta en consola
```

### Ejemplo Visual de una Sesión

```
📱 Tú > Listar mis campos

[22:15:30] 📱 WhatsApp → Webhook
👤 Usuario: Listar mis campos

[22:15:30] ⚙️  Sistema: Procesando en webhook... (validando, llamando OpenAI, ejecutando tools...)

[22:15:33] 📤 Webhook → Twilio → WhatsApp
🤖 Asistente: Aquí están tus campos:

1. Campo Norte - 150 hectáreas
2. Campo Sur - 200 hectáreas
3. La Esperanza - 100 hectáreas

Total: 3 campos, 450 hectáreas
   [Message SID: SM20260120221533123456]

📱 Tú > Crear un nuevo campo llamado San Jorge de 75 hectáreas

[22:16:10] 📱 WhatsApp → Webhook
👤 Usuario: Crear un nuevo campo llamado San Jorge de 75 hectáreas

[22:16:10] ⚙️  Sistema: Procesando en webhook... (validando, llamando OpenAI, ejecutando tools...)

[22:16:12] 📤 Webhook → Twilio → WhatsApp
🤖 Asistente: ✅ Campo creado exitosamente!

📋 Detalles:
- Nombre: San Jorge
- Superficie: 75 hectáreas
- ID: 15
   [Message SID: SM20260120221612789012]
```

## 🎨 Personalización

### Cambiar el Formato de Salida

Puedes modificar la función `print_message()` en `test_whatsapp_cli.py` para cambiar cómo se muestran los mensajes.

### Agregar Comandos Personalizados

En la función `main()`, puedes agregar más comandos especiales en la sección donde se procesan `'help'`, `'clear'`, etc.

## 📝 Notas Importantes

1. **No se envían mensajes reales**: Este simulador NO envía mensajes de WhatsApp reales. Solo simula el flujo interno.

2. **Sin validación de firma**: El simulador no incluye la firma de Twilio, pero el webhook está configurado para no validarla en modo DEBUG.

3. **Datos reales**: El simulador trabaja con la base de datos real, así que cualquier creación/modificación de datos es real.

4. **OpenAI real**: Las llamadas a OpenAI son reales y consumen créditos de tu cuenta.

## 🔗 Archivos Relacionados

- `test_whatsapp_cli.py`: Script principal del simulador
- `api/apis/whatsapp_api.py`: Webhook que recibe los mensajes
- `api/controllers/whatsapp_controller.py`: Controlador que procesa los mensajes
- `api/services/whatsapp_openai_agent.py`: Servicio que interactúa con OpenAI

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs en la consola
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que el servidor Django esté configurado correctamente
4. Revisa la documentación de cada servicio en los archivos mencionados arriba
