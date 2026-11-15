# CLAUDE.md — Lunar Landing Site Navigator (NASA Space Apps 2026)

Reglas generales del proyecto (compartidas con todas las IAs del equipo):
@AGENTS.md

Catálogo de APIs de la NASA del proyecto: `nasa_apis.csv` (la key va en `.env` como NASA_API_KEY; nunca en el código).

# Protocolo Maestro de Ingeniería, Apps e Investigación

## 1. Filosofía de Ejecución y Diseño
- **Demo-First & MVP Funcional:** Prioriza entregar un flujo extremo a extremo funcional y visualmente impecable antes de construir módulos secundarios, paneles admin o autenticación compleja.
- **Arquitectura Desacoplada:** Separa estrictamente la capa de procesamiento/datos (`/backend` en Python/FastAPI) de la interfaz interactiva (`/frontend` en React/Next.js + Tailwind CSS).
- **Resiliencia con Datos Reales:** Todo pipeline de datos externos (APIs NASA, sensores, web scraping) debe guardar un snapshot limpio en `/data/processed/` (`.parquet` o `.json` < 2 MB) para garantizar velocidad y funcionamiento offline.

## 2. Rigor Técnico, Científico y Cero Alucinaciones
- **Trazabilidad:** Cita siempre la fórmula matemática, norma técnica o fuente primaria en los docstrings de cada función analítica.
- **Unidades Explícitas:** Usa el Sistema Internacional (SI) e indica unidades en nombres de variables o comentarios (`_m_s`, `_hz`, `_km2`, `_kelvin`).
- **Baseline Antes de Complejidad:** Implementa primero un modelo interpretable o ecuación física validada (`XGBoost`, FFT, umbrales físicos) antes de entrenar redes neuronales pesadas.

## 3. Disciplina de Depuración y Seguridad
- **Loop de Debugging:** Reproducir -> Aislar -> Diagnosticar causa raíz -> Corregir -> Verificar con test. Nunca apliques parches a ciegas ni borres funcionalidades previas.
- **Seguridad:** Prohibido hardcodear API keys o subir archivos > 10 MB a Git. Usa `.env` y registra asistencia de IA en `AI_USAGE_LOG.md`.
