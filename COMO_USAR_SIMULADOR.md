# 🚀 GUÍA RÁPIDA - Cómo Usar el Simulador de WhatsApp

## Paso 1️⃣: Abrir Terminal

Abre PowerShell o CMD en la carpeta de tu proyecto:

```powershell
cd c:\Users\usuario\Repos\GesAgroBack
```

## Paso 2️⃣: Ejecutar el Simulador

```powershell
python test_whatsapp_cli.py
```

## Paso 3️⃣: Esperar que Inicie

Verás esto:

```
================================================================================
  🤖 SIMULADOR DE WHATSAPP - GEMINI CLI
================================================================================

✅ Usando automáticamente: admin@gesagro.com (+5493498416451)

📱 Tú >
```

## Paso 4️⃣: Escribir Mensajes

Simplemente escribe y presiona **Enter**:

```
📱 Tú > Hola, qué puedes hacer?
```

## Paso 5️⃣: Esperar Respuesta

El sistema procesará y responderá:

```
[22:30:13] 📤 Webhook → Twilio → WhatsApp
🤖 Asistente: ¡Hola! Puedo ayudarte a gestionar...

📱 Tú >
```

## Paso 6️⃣: Continuar Conversación

Sigue escribiendo:

```
📱 Tú > Listar mis campos
📱 Tú > Cuántos campos tengo?
📱 Tú > Crear un campo llamado Test de 50 hectáreas
```

## Paso 7️⃣: Salir

Para terminar, escribe:

```
📱 Tú > salir
```

O presiona **Ctrl + C**

---

## 💡 Ejemplos de Mensajes

### Consultas Básicas
```
Hola, qué puedes hacer?
Ayuda
```

### Listar Datos
```
Listar mis campos
Mostrar todas las máquinas
Cuáles son mis clientes?
Listar trabajos
```

### Crear Datos
```
Crear un campo llamado La Esperanza de 100 hectáreas
Agregar un nuevo cliente llamado Juan Pérez
Crear un trabajo de siembra en el campo Tononio
```

### Consultas Específicas
```
Cuántos campos tengo?
Cuántas hectáreas tengo en total?
Mostrar el campo Tononio
Información del cliente Stangaferro
```

---

## 🎯 Comandos Especiales

Dentro del simulador puedes usar:

- **`help`** - Muestra ayuda con ejemplos
- **`clear`** o **`cls`** - Limpia la pantalla
- **`salir`** o **`exit`** - Cierra el simulador

---

## ✅ Eso es Todo!

Es así de simple:

1. **Ejecutas** → `python test_whatsapp_cli.py`
2. **Escribes** → Tu mensaje + Enter
3. **Esperas** → La respuesta del asistente
4. **Repites** → Cuantas veces quieras
5. **Sales** → `salir` o Ctrl+C

**¡Disfruta! 🚀**
