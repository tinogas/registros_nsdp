"""Lógica de respaldos y restauración de la base de datos."""
import json
import shutil
import datetime
from pathlib import Path
from app.utils.config import DB_PATH, BACKUPS_DIR, BITACORA_PATH

_PREFIX = "registros_"
_SUFFIX = ".db"


# ── API pública ───────────────────────────────────────────────────────────────

def create_backup() -> tuple[bool, str]:
    """Crea un respaldo con marca de tiempo. Devuelve (ok, nombre_archivo|error)."""
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUPS_DIR / f"{_PREFIX}{ts}{_SUFFIX}"
    try:
        shutil.copy2(DB_PATH, dest)
        _log("Respaldo creado", dest.name, "OK", "")
        return True, dest.name
    except Exception as e:
        _log("Respaldo creado", dest.name, "ERROR", str(e))
        return False, str(e)


def restore_backup(backup_path: Path) -> tuple[bool, str]:
    """Reemplaza la BD activa con el respaldo indicado."""
    if not backup_path.exists():
        return False, "El archivo de respaldo no existe."
    try:
        shutil.copy2(backup_path, DB_PATH)
        _log("Restauración", backup_path.name, "OK", "")
        return True, backup_path.name
    except Exception as e:
        _log("Restauración", backup_path.name, "ERROR", str(e))
        return False, str(e)


def delete_backup(backup_path: Path) -> tuple[bool, str]:
    try:
        backup_path.unlink()
        _log("Respaldo eliminado", backup_path.name, "OK", "")
        return True, backup_path.name
    except Exception as e:
        return False, str(e)


def list_backups() -> list[Path]:
    """Lista los archivos de respaldo más recientes primero."""
    return sorted(BACKUPS_DIR.glob(f"{_PREFIX}*{_SUFFIX}"), reverse=True)


def get_log() -> list[dict]:
    if not BITACORA_PATH.exists():
        return []
    try:
        with open(BITACORA_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def clear_log() -> None:
    BITACORA_PATH.write_text("[]", encoding="utf-8")


# ── Interno ───────────────────────────────────────────────────────────────────

def _log(operacion: str, archivo: str, estado: str, mensaje: str) -> None:
    entries = get_log()
    entries.append({
        "fecha":     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "operacion": operacion,
        "archivo":   archivo,
        "estado":    estado,
        "mensaje":   mensaje,
    })
    with open(BITACORA_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
