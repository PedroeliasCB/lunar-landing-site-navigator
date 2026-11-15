---
name: scientific-validation
description: Validación matemática, física y trazabilidad científica para cumplir el criterio de Scientific Validity de los jueces de la NASA.
---

# Skill: Scientific Validation & Zero Hallucination

## Objetivo
Garantizar rigor técnico y científico comprobable en cada cálculo, índice espectral, modelo predictivo o simulación física.

## Reglas de Verificación
1. **Cita la fuente oficial:** En el docstring de cada función científica, incluye la ecuación matemática exacta y la referencia técnica (ej. ATBD de NASA MODIS/Landsat, documento técnico de JPL, o paper de referencia).
2. **Consistencia de unidades:** Especifica explícitamente las unidades SI en nombres de variables o comentarios (`_m_s`, `_km2`, `_kelvin`, `_w_m2`). Nunca mezcles unidades imperiales y métricas sin conversión explícita.
3. **Validación contra línea base:** Antes de entrenar redes neuronales complejas, implementa un baseline físico o estadístico interpretable (`XGBoost`, regresión física o umbral espectral estándar) y reporta métricas reales (RMSE, F1-Score, ROC-AUC).
4. **Tests unitarios obligatorios:** Crea pruebas en `tests/test_physics.py` con valores de entrada conocidos y rangos físicos válidos (ej. NDVI estrictamente entre -1.0 y 1.0).
