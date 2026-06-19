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
    print(f"Base de datos inicializada en: {DB_PATH}")


def count_all() -> dict:
    with db() as conn:
        return {
            "matrimonios":    conn.execute("SELECT count(*) FROM matrimonios").fetchone()[0],
            "primera_comunion": conn.execute("SELECT count(*) FROM primera_comunion").fetchone()[0],
            "confirmacion":   conn.execute("SELECT count(*) FROM confirmacion").fetchone()[0],
            "bautismos":      conn.execute("SELECT count(*) FROM bautismos").fetchone()[0],
            "catecumenos":    conn.execute("SELECT count(*) FROM catecumenos").fetchone()[0],
        }
