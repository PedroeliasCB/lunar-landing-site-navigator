---
name: demo-first-ideation
description: Estrategia de alcance y arquitectura enfocada en la demo en vivo de 2 minutos para NASA Space Apps Challenge. Activar al iniciar el proyecto o definir features.
---

# Skill: Demo-First Ideation (NASA Space Apps)

## Objetivo
Maximizar el puntaje en Impacto, Relevancia y Presentación evitando el sobre-ingenierizado en 48 horas.

## Reglas Estrictas
1. **Define el "Golden Path" primero:** Antes de crear bases de datos, autenticación o paneles de administración, escribe el guion exacto de 120 segundos que verá el juez en vivo.
2. **Cero fricción de usuario:** Prohibido implementar login/registro, gestión de roles o pantallas de carga largas. La aplicación debe abrir directamente en la visualización interactiva con un caso precargado listo para explorar.
3. **Arquitectura desacoplada:**
   - `/backend`: Scripts en Python que ingieren datos NASA y exportan JSON/Parquet estáticos o sirven endpoints ligeros en FastAPI.
   - `/frontend`: App web estática/SPA (React/Next.js + Tailwind) desplegable en Vercel/Netlify en 30 segundos.
4. **Métrica de impacto visible:** Toda pantalla principal debe mostrar al menos un KPI cuantitativo derivado de datos reales de la NASA (ej. área afectada en km², probabilidad de evento, reducción de tiempo de respuesta).
