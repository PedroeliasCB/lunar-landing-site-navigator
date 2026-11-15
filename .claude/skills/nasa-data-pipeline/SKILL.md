---
name: nasa-data-pipeline
description: Protocolo de ingesta, filtrado y caché local de datasets satelitales, astronómicos y de telemetría de la NASA sin saturar RAM ni tiempo de descarga.
---

# Skill: NASA Data Pipeline

## Objetivo
Extraer subconjuntos exactos de datos de la NASA (Earthdata, CMR, FIRMS, DONKI, NeoWs, MAST/TESS) y dejarlos listos para consumo rápido en backend y frontend.

## Reglas Operativas
1. **Nunca descargues datasets globales completos:** Usa siempre bounding boxes espaciales (`bbox`), ventanas temporales cortas (`temporal`), o peticiones HTTP con `Range headers` usando `earthaccess`, `astroquery` o `requests`.
2. **Caché obligatorio en disco:** Todo dato descargado y limpiado debe serializarse inmediatamente en `/data/processed/` en formato `.parquet` (para análisis) y `.json` ligero (< 2 MB, redondeando floats a 4-5 decimales) para el frontend.
3. **Librerías estándar aprobadas:**
   - Observación de la Tierra: `earthaccess`, `xarray`, `rioxarray`, `geopandas`, `rasterio`.
   - Astrofísica / Exoplanetas: `lightkurve`, `astropy`, `astroquery`.
   - Clima Espacial / Asteroides: NASA Open APIs (`DONKI`, `NeoWs`, `EONET`).
4. **Resiliencia en vivo:** Siempre guarda un fallback local (`demo_fallback.json`) con datos reales pre-procesados para que la demo jamás dependa de que una API externa responda durante la presentación ante los jueces.
