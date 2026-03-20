# 🔐 hexseg-mx — BI Geoespacial para Seguridad en México

> *"Business Intelligence es tener la inteligencia visual y conceptual de que una empresa sea exitosa."*

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Flet](https://img.shields.io/badge/Flet-UI_Framework-0077FF)](https://flet.dev)
[![H3](https://img.shields.io/badge/H3-Hexagons-FF6B6B)](https://uber.github.io/h3-py/)
[![License](https://img.shields.io/badge/License-CC--BY--SA-green)](./LICENSE)

---

## 🎯 ¿Qué es hexseg-mx?

Una herramienta de **Business Intelligence geoespacial** que analiza delitos en México usando:
- 🗺️ **Hexágonos H3** (Uber) para visualización de focos rojos
- 📊 **Índice de delincuencia** por municipio (delitos / habitantes)
- 🔗 **Enlaces compartibles** de Google Maps para cada foco de riesgo
- 🎯 **Filtros interactivos** por estado, año, tipo de delito y municipio

**Construido en 65 días** siguiendo el método MAHE:  
👉 [github.com/crosasr/mahe-aprendizaje-estrategico](https://github.com/crosasr/mahe-aprendizaje-estrategico)

---

## 🚀 Características

| Función | Descripción |
|---------|-------------|
| 📍 **Mapa Hexagonal** | Visualización de riesgos con hexágonos H3 (resolución 8) |
| 🔴 **Focos Rojos** | Índice > 1.0 = riesgo alto (rojo), > 0.5 = riesgo medio (naranja) |
| 🔗 **Links Compartibles** | Cada hexágono genera enlace de Google Maps para reportar |
| 📈 **KPIs en Tiempo Real** | Total delitos, focos rojos, top 5 municipios |
| 🎚️ **Filtros Interactivos** | Estado, año, tipo de delito, municipio |
| 📊 **Tabla de Datos** | Lista completa de focos rojos con índices |

---

## 🛠️ Requisitos

```bash
Python 3.12+
pip install pandas folium h3 flet