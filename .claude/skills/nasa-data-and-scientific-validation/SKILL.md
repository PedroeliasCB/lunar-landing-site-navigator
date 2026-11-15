---
name: nasa-data-and-scientific-validation
description: Ingesta optimizada de datos satelitales/astronómicos (NASA Earthdata, FIRMS, DONKI, TESS) y validación matemática/física.
---

# Skill: NASA Data Pipeline & Scientific Validation
1. **Subsetting Inteligente:** Nunca descargues datasets globales completos. Filtra siempre por bounding box espacial (`bbox`), ventana temporal o `Range headers` usando `earthaccess`, `astroquery` o `requests`.
2. **Caché y Fallback:** Serializa los datos limpios en `/data/processed/` en formato `.parquet` y `.json` ligero (< 2 MB, redondeando floats a 4-5 decimales).
3. **Validación Física:** Documenta la ecuación oficial en cada función, respeta unidades SI y crea tests unitarios en `tests/test_physics.py` verificando rangos físicos válidos (ej. NDVI entre -1 y 1).
4. **Transparencia de IA:** Actualiza `AI_USAGE_LOG.md` documentando qué módulos fueron asistidos por IA y cuáles fueron validados por ingeniería humana.
