# 🔐 SafeHex MX — BI Geoespacial para Seguridad en México

> *"Business Intelligence es tener la inteligencia visual y conceptual de que una empresa sea exitosa."*

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Flet](https://img.shields.io/badge/Flet-UI_Framework-0077FF)](https://flet.dev)
[![H3](https://img.shields.io/badge/H3-Hexagons-FF6B6B)](https://uber.github.io/h3-py/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57)](https://sqlite.org)

---

## 🎯 ¿Qué es SafeHex MX?

Una herramienta de **Business Intelligence geoespacial** de alto nivel diseñada para PyMEs y consultoría de seguridad en México. Analiza la incidencia delictiva mediante:
- 🗺️ **Hexágonos H3 (Uber)**: Visualización de micro-zonas de riesgo con resolución nivel 8.
- 📊 **Arquitectura Modular**: Disección de componentes para alta disponibilidad y escalabilidad móvil.
- ⚡ **Motor SQLite**: Consultas optimizadas que eliminan la carga pesada de memoria RAM.
- 🔗 **Geointeligencia**: Enlaces directos a Google Maps para logística y toma de decisiones en tiempo real.

**Construido siguiendo el método MAHE** para un aprendizaje estratégico y profesional.

---

## 🏗️ Arquitectura del Sistema (La Disección)

El proyecto ha sido refactorizado siguiendo el principio de **Separación de Responsabilidades** para garantizar un mantenimiento de grado empresarial:

| Módulo | Función |
| :--- | :--- |
| `app.py` | Orquestador principal de la aplicación. |
| `ui.py` | Interfaz moderna y responsiva construida con **Flet**. |
| `database.py` | Gestor de persistencia en **SQLite** (Adiós al cuello de botella de CSV). |
| `processor.py` | Lógica de limpieza, normalización y reglas de negocio. |
| `map_generator.py` | Motor de generación geoespacial y capas H3. |
| `validator.py` | Sistema de monitoreo de rendimiento y saneamiento de datos. |
| `logger.py` | Historial de operaciones y auditoría técnica. |



---

## 🚀 Características de Élite

- 🔴 **Detección de Focos Rojos**: Algoritmo que calcula el índice de delincuencia relativo (Delitos/Población).
- 📅 **Análisis Histórico**: Cobertura de datos oficiales (SESNSP) desde 2015 hasta 2025.
- 📱 **Mobile Ready**: Estructura preparada para compilación en Android e iOS.
- 🛡️ **Seguridad de Datos**: Saneamiento de entradas para prevenir inyecciones y errores de consistencia.

---

## ⚖️ Licencia y Responsabilidad

### Licencia
Este proyecto se distribuye bajo la **Licencia MIT**. Esto permite su uso comercial y modificación, manteniendo la atribución al autor original.

### Descargo de Responsabilidad (Disclaimer)
**SafeHex MX** es una herramienta informativa basada en datos públicos oficiales (SESNSP e INEGI). 
1. Los resultados son proyecciones estadísticas y no garantizan condiciones de seguridad absoluta.
2. El uso de esta información para decisiones logísticas o de inversión es responsabilidad exclusiva del usuario.
3. El autor no se hace responsable por el mal uso de la plataforma o por discrepancias en las fuentes de datos oficiales.

---

## 👤 Autor
**César Victorio Rosas Ramos** *Desarrollador de Soluciones de Inteligencia Estratégica*

---
