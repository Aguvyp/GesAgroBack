# 🔄 Mejoras de Verificación y Confirmación - Implementadas

## 📋 Resumen

He actualizado el agente de OpenAI para que sea más cuidadoso al crear y actualizar registros, verificando duplicados y solicitando datos faltantes.

---

## ✅ Cambios Implementados

### 1. **System Prompt Mejorado**

Actualicé el system prompt con reglas claras de verificación y confirmación:

```
REGLAS CRÍTICAS DE VERIFICACIÓN Y CONFIRMACIÓN:

1. ANTES DE CREAR O ACTUALIZAR:
   - SIEMPRE verifica primero si ya existe un registro similar usando get_*
   - Si encuentras un registro similar, pregunta al usuario si desea:
     a) Actualizar el registro existente
     b) Crear uno nuevo de todas formas
     c) Cancelar la operación

2. DATOS FALTANTES:
   - Si faltan datos REQUERIDOS, pregunta al usuario por ellos ANTES de ejecutar
   - Si tienes dudas sobre qué acción realizar, pregunta al usuario para confirmar
   - Nunca asumas datos que no fueron proporcionados explícitamente

3. VERIFICACIÓN DE DUPLICADOS:
   - Para CAMPOS: Verifica por nombre similar
   - Para CLIENTES: Verifica por nombre o CUIT
   - Para PERSONAL: Verifica por nombre o DNI
   - Para TRABAJOS: Verifica por campo + tipo_trabajo + fecha_inicio
   - Para COSTOS: Verifica por destinatario + monto + fecha
```

### 2. **Descripciones de Tools Actualizadas**

Actualicé las descripciones de las tools de creación para ser más explícitas:

#### **`create_campo`**:
```
IMPORTANTE: ANTES de crear, SIEMPRE llama primero a get_campos para verificar 
si ya existe un campo con nombre similar. Si existe, pregunta al usuario si 
desea actualizar el existente o crear uno nuevo.
```

#### **`create_cliente`**:
```
IMPORTANTE: ANTES de crear, SIEMPRE llama primero a get_clientes para verificar 
si ya existe un cliente con nombre o CUIT similar. Si existe, pregunta al usuario 
si desea actualizar el existente o crear uno nuevo.
```

#### **`create_personal`**:
```
IMPORTANTE: ANTES de crear, SIEMPRE llama primero a get_personal para verificar 
si ya existe personal con nombre o DNI similar. Si existe, pregunta al usuario 
si desea actualizar el existente o crear uno nuevo. Si faltan datos opcionales 
(DNI, teléfono), pregunta al usuario si desea proporcionarlos antes de crear.
```

### 3. **Ejemplos de Flujo en el Prompt**

Agregué ejemplos concretos de cómo debe comportarse:

```
Usuario: "Crear campo La Esperanza"
Asistente: [Primero llama get_campos para verificar]
- Si NO existe: Procede a crear
- Si existe: "Ya existe un campo llamado 'La Esperanza' con 100 hectáreas. 
             ¿Deseas actualizar ese campo o crear uno nuevo?"

Usuario: "Agregar personal Juan Pérez"
Asistente: [Primero llama get_personal para verificar]
- Si NO existe: "¿Podrías proporcionarme el DNI y teléfono de Juan Pérez? 
                (opcional pero recomendado)"
- Si existe: "Ya existe un personal llamado 'Juan Pérez' con DNI 12345678. 
             ¿Deseas actualizar sus datos o crear un nuevo registro?"
```

---

## ⚠️ Limitaciones Actuales

### **OpenAI decide cuándo llamar funciones**

Aunque hemos instruido al agente para que SIEMPRE verifique duplicados, **OpenAI (el modelo) decide autónomamente qué funciones llamar y en qué orden**.

**Esto significa:**
- ✅ El agente **puede** verificar duplicados si lo considera necesario
- ⚠️ El agente **puede decidir** crear directamente si cree que es lo correcto
- ⚠️ No hay garantía 100% de que siempre verifique primero

**Ejemplo observado:**
```
> Crear un campo llamado Tononio
🤖 El campo llamado "Tononio" ha sido creado exitosamente.
```
(No verificó que ya existía un campo "Tononio")

### **¿Por qué sucede esto?**

1. **Autonomía del modelo**: GPT-4 decide qué funciones llamar basándose en el contexto
2. **Interpretación del mensaje**: Si el mensaje es muy directo ("Crear..."), puede interpretarlo como una orden directa
3. **Optimización**: El modelo puede decidir que verificar no es necesario si el usuario fue explícito

---

## 💡 Mejoras Adicionales Posibles

Si necesitas garantizar 100% la verificación de duplicados, hay 3 opciones:

### **Opción 1: Validación en el Backend (Recomendado)**

Modificar las funciones `create_*` para que verifiquen duplicados automáticamente:

```python
elif function_name == "create_campo":
    # Verificar si ya existe un campo con ese nombre
    existing = Campo.objects.filter(
        nombre__iexact=arguments['nombre'],
        usuario_id=usuario_id
    ).first()
    
    if existing:
        return {
            "error": f"Ya existe un campo llamado '{existing.nombre}' con {existing.hectareas} hectáreas. "
                    f"Si deseas actualizarlo, usa update_campo con ID {existing.id}. "
                    f"Si deseas crear uno nuevo de todas formas, confirma explícitamente."
        }
    
    # Continuar con la creación...
```

### **Opción 2: Mensajes más Específicos del Usuario**

Entrenar a los usuarios a ser más específicos:
```
❌ "Crear campo La Esperanza"
✅ "Verificar si existe campo La Esperanza, si no existe crearlo"
✅ "Quiero crear un nuevo campo La Esperanza, verifica primero si ya existe"
```

### **Opción 3: Flujo de Dos Pasos Forzado**

Modificar el agente para que SIEMPRE requiera confirmación:
- Primera llamada: Verificar y preguntar
- Segunda llamada: Crear con confirmación explícita

---

## 🎯 Comportamiento Actual vs Esperado

### **Comportamiento Actual:**
```
Usuario: "Crear personal Juan Pérez"
Agente: [Puede o no verificar duplicados]
        "Personal 'Juan Pérez' creado exitosamente"
```

### **Comportamiento Mejorado (con las instrucciones):**
```
Usuario: "Crear personal Juan Pérez"
Agente: [Debería verificar primero]
        "¿Podrías proporcionarme el DNI y teléfono de Juan Pérez?"
```

### **Comportamiento Ideal (con validación backend):**
```
Usuario: "Crear personal Juan Pérez"
Agente: [Intenta crear]
Backend: [Verifica automáticamente]
        "Ya existe un personal llamado 'Juan Pérez' con DNI 12345678.
         ¿Deseas actualizar ese registro (ID: 5) o crear uno nuevo?"
```

---

## 📝 Recomendación

Para tu caso de uso, recomiendo **implementar la Opción 1 (Validación en el Backend)** porque:

✅ Garantiza 100% la verificación  
✅ No depende de las decisiones del modelo de IA  
✅ Proporciona mensajes de error claros  
✅ Permite al usuario decidir explícitamente qué hacer  

¿Quieres que implemente esta validación en el backend para las funciones de creación?

---

## 🚀 Estado Actual

**Implementado:**
- ✅ System prompt con reglas de verificación
- ✅ Descripciones de tools actualizadas
- ✅ Ejemplos de flujo correcto
- ✅ Instrucciones para solicitar datos faltantes

**Pendiente (opcional):**
- ⏳ Validación de duplicados en el backend (garantiza 100%)
- ⏳ Confirmación forzada para operaciones críticas
- ⏳ Mensajes de error más descriptivos con sugerencias

---

## 📚 Archivos Modificados

1. **`api/services/opencode_agent.py`**:
   - System prompt actualizado (líneas ~1114-1167)
   - Descripciones de `create_campo`, `create_cliente`, `create_personal` actualizadas

---

**¡Las mejoras están implementadas y listas para usar!** 🎉

El agente ahora tiene instrucciones claras para verificar duplicados y solicitar datos faltantes, aunque la decisión final de cuándo hacerlo la toma el modelo de OpenAI.
