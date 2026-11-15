# Reglas Maestras del Proyecto — NASA Space Apps Challenge

Este archivo es leído automáticamente por **Claude Code, Google Antigravity, Cursor, Hermes Agent, Codex** y sirve como **System Prompt / Custom Instructions** para **ChatGPT, Gemini Web y DeepSeek**.

## 1. Filosofía de Ejecución (48 Horas)
- **Demo-First:** Todo código debe servir directamente a la demostración interactiva de 2 minutos. Cero autenticación compleja o pantallas innecesarias.
- **Datos Reales + Fallback:** Descarga subconjuntos filtrados de la NASA (`earthaccess`, `astroquery`, NASA APIs) y guarda siempre un archivo `.json` ligero (< 2 MB) en `/data/processed/` para garantizar respuesta instantánea en vivo.

## 2. Rigor Científico (Cero Alucinaciones)
- Cita siempre la fórmula física o documento oficial de la NASA en los docstrings.
- Especifica unidades SI en todas las variables científicas.
- Implementa primero un modelo baseline interpretable (`XGBoost` o ecuación física) antes de redes neuronales complejas.

## 3. Seguridad y Transparencia NASA
- Nunca subas API Keys ni archivos crudos > 10 MB al repositorio.
- Documenta toda asistencia de IA en `AI_USAGE_LOG.md` para la sección obligatoria de uso de IA del proyecto.
