import sqlite3
from contextlib import contextmanager
from app.utils.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS matrimonios (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            numero       TEXT,
            pareja       TEXT,
            dia          TEXT,
            mes          TEXT,
            anio         TEXT,
            presbitero   TEXT,
            testigo1     TEXT,
            testigo2     TEXT,
            testigo3     TEXT,
            testigo4     TEXT,
            parroco      TEXT,
            libro        TEXT,
            pagina       TEXT,
            partida      TEXT,
            dias_extra   TEXT,
            mes_extra    TEXT,
            fuente_archivo TEXT
        );

        CREATE TABLE IF NOT EXISTS primera_comunion (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT,
            dia            TEXT,
            mes            TEXT,
            anio           TEXT,
            mama           TEXT,
            papa           TEXT,
            padrinos       TEXT,
            parroco        TEXT,
            fuente_archivo TEXT
        );

        CREATE TABLE IF NOT EXISTS confirmacion (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            numero         TEXT,
            nombre         TEXT,
            dia            TEXT,
            mes            TEXT,
            anio           TEXT,
            papa           TEXT,
            mama           TEXT,
            padrinos       TEXT,
            arzobispo      TEXT,
            parroco        TEXT,
            libro          TEXT,
            pagina         TEXT,
            partida        TEXT,
            fuente_archivo TEXT
        );

        CREATE TABLE IF NOT EXISTS bautismos (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre            TEXT,
            dia_nacimiento    TEXT,
            mes_nacimiento    TEXT,
            anio_nacimiento   TEXT,
            lugar_nacimiento  TEXT,
            papa              TEXT,
            mama              TEXT,
            dia_bautismo      TEXT,
            mes_bautismo      TEXT,
            anio_bautismo     TEXT,
            ministro          TEXT,
            padrino           TEXT,
            madrina           TEXT,
            parroco           TEXT,
            registro_no       TEXT,
            libro             TEXT,
            pagina            TEXT,
            acta              TEXT,
            fuente_archivo    TEXT
        );

        CREATE TABLE IF NOT EXISTS catecumenos (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT,
            dia            TEXT,
            mes            TEXT,
            anio           TEXT,
            padre          TEXT,
            madre          TEXT,
            padrinos       TEXT,
            fuente_archivo TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_matrimonios_pareja   ON matrimonios(pareja);
        CREATE INDEX IF NOT EXISTS idx_comunion_nombre      ON primera_comunion(nombre);
        CREATE INDEX IF NOT EXISTS idx_confirmacion_nombre  ON confirmacion(nombre);
        CREATE INDEX IF NOT EXISTS idx_bautismos_nombre     ON bautismos(nombre);
        CREATE INDEX IF NOT EXISTS idx_catecumenos_nombre   ON catecumenos(nombre);
        """)
    _migrate_folio_columns()
    homologar_parrocos()
    print(f"Base de datos inicializada en: {DB_PATH}")


# Columna de año por tabla (para partición del folio)
_YEAR_COL = {
    "matrimonios":      "anio",
    "primera_comunion": "anio",
    "confirmacion":     "anio",
    "bautismos":        "anio_bautismo",
    "catecumenos":      "anio",
}

TABLES = list(_YEAR_COL.keys())


def _migrate_folio_columns():
    """Agrega la columna folio a las tablas que aún no la tienen."""
    with db() as conn:
        for table in TABLES:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN folio INTEGER")
            except Exception:
                pass  # columna ya existe


def recalculate_folios(table: str):
    """
    Asigna folios secuenciales por año, reiniciando en 1 cada año.
    Ordenamiento dentro del año: por id de inserción.
    """
    year_col = _YEAR_COL.get(table, "anio")
    with db() as conn:
        conn.executescript(f"""
        WITH ranked AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY {year_col}
                       ORDER BY id
                   ) AS rn
            FROM {table}
            WHERE {year_col} IS NOT NULL
        )
        UPDATE {table}
        SET folio = (SELECT rn FROM ranked WHERE ranked.id = {table}.id);
        """)


def recalculate_all_folios():
    for table in TABLES:
        recalculate_folios(table)


_TABLES_WITH_PARROCO = ["bautismos", "confirmacion", "matrimonios", "primera_comunion"]

# (nombre_canónico, patrón LIKE para detectar variantes)
_CANONICAL_PARROCOS = [
    ("PBRO. FELIPE DE JESUS ZARAGOZA ORTEGA", "%ZARAGOZA%"),
    ("PBRO. GERARDO CAMACHO PONCE",           "%CAMACHO%"),
]


def homologar_parrocos():
    """Normaliza todas las variantes tipográficas de párroco a la forma canónica."""
    with db() as conn:
        for table in _TABLES_WITH_PARROCO:
            for canonical, pattern in _CANONICAL_PARROCOS:
                conn.execute(
                    f"UPDATE {table} SET parroco = ? "
                    f"WHERE parroco LIKE ? AND parroco != ?",
                    (canonical, pattern, canonical),
                )


def count_all() -> dict:
    with db() as conn:
        return {
            "matrimonios":    conn.execute("SELECT count(*) FROM matrimonios").fetchone()[0],
            "primera_comunion": conn.execute("SELECT count(*) FROM primera_comunion").fetchone()[0],
            "confirmacion":   conn.execute("SELECT count(*) FROM confirmacion").fetchone()[0],
            "bautismos":      conn.execute("SELECT count(*) FROM bautismos").fetchone()[0],
            "catecumenos":    conn.execute("SELECT count(*) FROM catecumenos").fetchone()[0],
        }
