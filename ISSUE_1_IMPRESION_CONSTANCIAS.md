# Issue #1 — Impresión de Constancias

**Repositorio:** tinogas/registros_nsdp  
**Estado:** Abierto  
**Autor:** tinogas  
**Fecha:** 19 de junio de 2026  
**URL:** https://github.com/tinogas/registros_nsdp/issues/1

---

## Descripción

Desarrollar una aplicación en Python para gestionar e imprimir constancias de sacramentos a partir de los registros existentes en los archivos Excel del repositorio.

Los archivos de datos de origen son:

| Archivo | Período |
|---|---|
| `SACRAMENTOS 2010 AL 2022 .xlsx` | 2010 – 2022 |
| `SACRAMENTOS 2023.xlsx` | 2023 |

Ambos archivos contienen pestañas independientes por tipo de sacramento:

- Matrimonios
- Primera Comunión
- Confirmación
- Bautizos
- Catecúmenos

---

## Requisitos funcionales

### 1. Captura de datos
- Formulario de ingreso/edición de registros sacramentales por tipo de sacramento.
- Persistencia de los datos en los archivos Excel existentes (o en una base de datos nueva si se decide migrar).

### 2. Impresión de constancias
- Generación de constancias individuales por sacramento.
- El formato de impresión debe poder adaptarse a distintos tipos de papel o plantillas preexistentes (p. ej. hojas membretadas de la parroquia).
- Los campos de la constancia deben poder reposicionarse según las necesidades del operador.

### 3. Módulo de reportes
- Reportes filtrables por tipo de sacramento, año, nombre, etc.
- Múltiples formatos de salida (PDF, Excel, impresión directa).
- Diseño personalizable del reporte.

---

## Alcance técnico sugerido

| Componente | Tecnología propuesta |
|---|---|
| Lenguaje | Python 3.x |
| Interfaz gráfica | Tkinter / PyQt / wxPython |
| Lectura/escritura Excel | `openpyxl` o `pandas` |
| Generación de PDF | `reportlab` o `WeasyPrint` |
| Impresión directa | `win32print` (Windows) |

---

## Criterios de aceptación

- [ ] La aplicación lee correctamente los registros de los dos archivos Excel existentes.
- [ ] El usuario puede buscar y seleccionar un registro para generar su constancia.
- [ ] La constancia generada puede imprimirse o exportarse a PDF.
- [ ] Los campos de la constancia son reposicionables desde la interfaz.
- [ ] El módulo de reportes permite filtrar y exportar en al menos dos formatos.
- [ ] La aplicación funciona en Windows (entorno de uso actual).

---

## Notas

- Los datos históricos (2010–2022) están consolidados en un solo archivo; los datos de 2023 están en un archivo separado. La aplicación debe manejar ambas fuentes de forma transparente.
- No existe código fuente previo en el repositorio; este issue representa el punto de partida del desarrollo.
