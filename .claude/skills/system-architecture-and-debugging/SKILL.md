---
name: system-architecture-and-debugging
description: Arquitectura modular de aplicaciones Full-Stack y protocolo estricto de resolución de errores sin regresiones.
---

# Skill: System Architecture & Disciplined Debugging
## Arquitectura
1. Define contratos de datos explícitos (esquemas Pydantic en FastAPI y tipos TypeScript en Frontend) antes de escribir lógica de negocio.
2. Mantén funciones puras y modulares (< 60 líneas por función) separando ingesta, transformación, modelado y exposición API.
## Protocolo de Debugging (4 Pasos Obligatorios)
1. **Reproducir:** Ejecuta el comando o test exacto que falla y captura el traceback completo.
2. **Aislar:** Identifica el módulo, línea y estado de variables exacto donde ocurre la desviación.
3. **Diagnosticar:** Explica la causa raíz técnica (ej. mismatch de dimensiones, tipo nulo, CORS, async sin await) antes de tocar el código.
4. **Verificar:** Aplica la corrección mínima necesaria y ejecuta pruebas automatizadas para confirmar que no se rompieron otros módulos.
