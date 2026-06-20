# NSDP — Sistema de Registros Sacramentales

Sistema de escritorio para la gestión de registros sacramentales de la **Parroquia Nuestra Señora de la Paz**, Hermosillo, Sonora.

---

## Descripción general

NSDP permite registrar, buscar, reportar e imprimir constancias de los cinco sacramentos que administra la parroquia:

| Sacramento | Tabla SQLite |
|---|---|
| Bautismos | `bautismos` |
| Primera Comunión | `primera_comunion` |
| Confirmación | `confirmacion` |
| Matrimonios | `matrimonios` |
| Catecúmenos | `catecumenos` |

---

## Requisitos del sistema

- Windows 10 / 11 (64 bits)
- Python 3.11+ (solo para desarrollo)
- Impresora configurada en el sistema (para imprimir constancias)

---

## Instalación

### Opción A — Ejecutable (usuarios finales)

1. Copiar `NSDP.exe` a la carpeta deseada (p. ej. `C:\Parroquia\NSDP\`).
2. Ejecutar `NSDP.exe`.
3. En el primer arranque se crean automáticamente las carpetas `data\` y `assets\` junto al ejecutable.
4. Colocar los archivos de plantilla de formularios en la misma carpeta del ejecutable:
   - `Formato_Bautizo.jpg`
   - `Formato_1ra_Comunion.jpg`
   - `Formato_confirmacion.jpg`
   - `Formato_matrimonio.jpg`

> Los archivos de plantilla ya están incluidos dentro del ejecutable.

### Opción B — Desde el código fuente (desarrolladores)

```bat
git clone https://github.com/tinogas/registros_nsdp.git
cd registros_nsdp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

---

## Estructura del proyecto

```
NSDP/
├── app/
│   ├── core/
│   │   ├── database.py      # Conexión SQLite, init_db, migraciones, folios
│   │   ├── models.py        # Dataclasses por sacramento
│   │   ├── importer.py      # Importación desde Excel (.xlsx)
│   │   ├── iglesia.py       # Configuración de la parroquia (JSON)
│   │   └── backup.py        # Respaldos, restauración, bitácora
│   ├── pdf/
│   │   ├── renderer.py      # Generación de constancias PDF (ReportLab)
│   │   ├── layout_editor.py # Carga/guarda posiciones de campos en JSON
│   │   └── templates.py     # Definición de campos por sacramento
│   ├── ui/
│   │   ├── app_window.py    # Ventana principal, pestañas, dashboard
│   │   ├── search_view.py   # Listado + búsqueda + formulario CRUD
│   │   ├── report_view.py   # Filtros, totales, exportación PDF/Excel
│   │   ├── print_view.py    # Editor visual de posición e impresión directa
│   │   ├── form_view.py     # Formulario de captura/edición de registros
│   │   ├── import_view.py   # Importación guiada desde Excel
│   │   ├── settings_view.py # Configuración de datos de la parroquia
│   │   └── backup_view.py   # Interfaz de respaldos y bitácora
│   ├── utils/
│   │   └── config.py        # Rutas, modo frozen (exe), directorios
│   └── main.py              # Punto de entrada
├── data/                    # Creado automáticamente en primer arranque
│   ├── registros.db         # Base de datos SQLite (modo WAL)
│   ├── iglesia.json         # Datos de la parroquia
│   ├── backups/             # Respaldos .db + bitácora.json
│   ├── layouts/             # Posiciones de campos por sacramento (JSON)
│   └── excel_backup/        # Copias de los Excel importados
├── assets/                  # Creado automáticamente
│   ├── logo_parroquia.png   # Logo (subido por el usuario vía Configuración)
│   └── foto_parroquia.jpg   # Foto exterior
├── Formato_Bautizo.jpg      # Plantillas de formularios físicos pre-impresos
├── Formato_1ra_Comunion.jpg
├── Formato_confirmacion.jpg
├── Formato_matrimonio.jpg
├── requirements.txt
└── build_exe.spec           # Configuración de PyInstaller
```

---

## Módulos principales

### `app/core/database.py`

- **`init_db()`** — Crea las tablas si no existen, ejecuta migraciones de columna `folio`, y normaliza nombres de párrocos.
- **`db()`** — Context manager para conexiones SQLite con commit automático y rollback en error.
- **`recalculate_folios(table)`** — Asigna folios secuenciales por año usando `ROW_NUMBER()`.
- **`homologar_parrocos()`** — Normaliza variantes tipográficas de los dos párrocos históricos a la forma canónica usando `LIKE`.

### `app/core/iglesia.py`

Maneja el archivo `data/iglesia.json` con los datos institucionales:

| Campo | Descripción |
|---|---|
| nombre | Nombre completo de la parroquia |
| ciudad | Ciudad y estado |
| direccion | Dirección postal |
| codigo_postal | CP |
| parroco_actual | Nombre del párroco en funciones |
| telefono | Teléfono de la oficina |
| horario_oficina | Horario de atención |
| secretaria | Nombre de la secretaria |
| email | Correo electrónico |
| facebook | Página de Facebook |
| instagram | Cuenta de Instagram |
| logo_file | Nombre del archivo de logo en `assets/` |
| foto_file | Nombre del archivo de foto en `assets/` |

### `app/core/backup.py`

- **`create_backup()`** — Copia `registros.db` a `data/backups/registros_YYYYMMDD_HHMMSS.db`.
- **`restore_backup(path)`** — Reemplaza la BD activa con el respaldo indicado.
- **`list_backups()`** — Lista los archivos de respaldo del más reciente al más antiguo.
- Toda operación queda registrada en `data/backups/bitacora.json`.

### `app/pdf/renderer.py`

- **`generate_pdf(table, data, output_path)`** — Genera una constancia oficial en PDF tamaño carta vertical.
- **`generate_form_pdf(table, data, output_path)`** — Genera un PDF con solo los valores de texto, para imprimir sobre formularios pre-impresos.
- **`print_pdf(path)`** — Envía el PDF directamente a la impresora predeterminada del sistema (sin abrir visor). Devuelve el nombre de la impresora usada.

### `app/ui/app_window.py`

Ventana principal (1200×720, redimensionable). Contiene:
- **Cabecera**: título, botón "Reportes", botón "Importar Excel", botón ⚙ (menú desplegable).
- **Menú ⚙**: Datos de la Parroquia | Importar Excel | Respaldos y Restauración.
- **Barra de pestañas**: Inicio + cinco sacramentos.
- **Área de contenido**: intercambia vistas según la pestaña activa.

### `app/ui/search_view.py`

Vista de listado para cada sacramento:
- Muestra 5 columnas: Folio, Nombre/Pareja, Día, Mes, Año.
- Búsqueda en tiempo real por cualquier campo.
- Doble clic en una fila abre el detalle completo del registro.
- Botones: Nuevo, Editar, Imprimir constancia, Imprimir en formulario, Eliminar.

### `app/ui/report_view.py`

Generación de reportes con:
- Filtros por año, párroco y sacramento.
- Vista treeview con subtotales por párroco y total general.
- Exportación a PDF (con sección de totales) y Excel (con cortes de grupo por párroco).
- Orden: párroco → año → folio.

### `app/ui/print_view.py`

Editor visual de posición de campos para las constancias:
- Panel izquierdo: preview a escala de la constancia o del formulario físico.
- Panel derecho: coordenadas X/Y editables por campo.
- Drag & drop de campos en el preview.
- Modo formulario: muestra la imagen del formulario pre-impreso como guía.
- **Impresión directa** a la impresora predeterminada (sin visor PDF intermedio).
- Las posiciones se guardan por sacramento en `data/layouts/`.

### `app/ui/backup_view.py`

Diálogo de respaldos (920×520):
- Panel izquierdo: lista de respaldos disponibles.
  - **Crear respaldo** — genera copia con marca de tiempo.
  - **Restaurar desde lista** — restaura el respaldo seleccionado en la lista.
  - **Restaurar desde archivo…** — abre un selector de archivo para restaurar cualquier `.db` del sistema.
  - **⬇ Guardar como…** — exporta el respaldo a cualquier ubicación.
  - **Eliminar** — borra el respaldo seleccionado.
- Panel derecho: bitácora de operaciones (fecha, operación, estado OK/ERROR).

---

## Base de datos — Esquema

### `bautismos`
`id, nombre, dia_nacimiento, mes_nacimiento, anio_nacimiento, lugar_nacimiento, papa, mama, dia_bautismo, mes_bautismo, anio_bautismo, ministro, padrino, madrina, parroco, registro_no, libro, pagina, acta, folio, fuente_archivo`

### `primera_comunion`
`id, nombre, dia, mes, anio, mama, papa, padrinos, parroco, folio, fuente_archivo`

### `confirmacion`
`id, numero, nombre, dia, mes, anio, papa, mama, padrinos, arzobispo, parroco, libro, pagina, partida, folio, fuente_archivo`

### `matrimonios`
`id, numero, pareja, dia, mes, anio, presbitero, testigo1, testigo2, testigo3, testigo4, parroco, libro, pagina, partida, dias_extra, mes_extra, folio, fuente_archivo`

### `catecumenos`
`id, nombre, dia, mes, anio, padre, madre, padrinos, folio, fuente_archivo`

> `folio`: número secuencial por año dentro de cada sacramento, calculado automáticamente.
> `fuente_archivo`: nombre del archivo Excel del que proviene el registro (si fue importado).

---

## Párrocos históricos

El sistema reconoce y normaliza automáticamente todas las variantes tipográficas de los dos párrocos:

| Forma canónica | Patrón de detección |
|---|---|
| PBRO. FELIPE DE JESUS ZARAGOZA ORTEGA | `%ZARAGOZA%` |
| PBRO. GERARDO CAMACHO PONCE | `%CAMACHO%` |

---

## Importación de datos desde Excel

Menú ⚙ → **Importar Excel**:
1. Seleccionar el archivo `.xlsx`.
2. El importador detecta las hojas por nombre y mapea las columnas automáticamente.
3. Los registros importados conservan el nombre del archivo de origen en `fuente_archivo`.
4. Se recalculan los folios al finalizar.

---

## Configuración de la parroquia

Menú ⚙ → **Datos de la Parroquia**:
- Captura nombre, dirección, teléfono, redes sociales, logo y foto.
- El logo aparece en el dashboard y en las constancias PDF.
- Los datos se guardan en `data/iglesia.json`.

---

## Respaldos y restauración

Menú ⚙ → **Respaldos y Restauración**:
- Los respaldos se almacenan en `data/backups/` con nombre `registros_YYYYMMDD_HHMMSS.db`.
- La restauración reemplaza la BD activa; se recomienda reiniciar la app después.
- Se puede restaurar desde la lista de respaldos locales O desde cualquier archivo `.db` del sistema (útil para restaurar en otro equipo).
- Toda operación queda en `data/backups/bitacora.json`.

---

## Generación del ejecutable

```bat
.venv\Scripts\activate
pyinstaller build_exe.spec --clean --noconfirm
```

El ejecutable se genera en `dist\NSDP.exe` (~24 MB). Incluye:
- CustomTkinter con todos sus temas
- Pillow, ReportLab, openpyxl, pywin32
- Plantillas de formularios (`Formato_*.jpg`)

**Archivos adicionales junto al exe** (no incluidos en el bundle):
- `data\` — creado automáticamente en primer arranque
- `assets\` — creado automáticamente; el usuario sube su logo

---

## Dependencias

```
customtkinter>=5.2.2
openpyxl>=3.1.2
reportlab>=4.1.0
Pillow>=10.3.0
pywin32>=306
pyinstaller>=6.6.0
```

---

## Repositorio

[https://github.com/tinogas/registros_nsdp](https://github.com/tinogas/registros_nsdp)

Rama principal de desarrollo: `creacion-de-sistema`
