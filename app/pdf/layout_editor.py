"""
Persistencia de layouts de constancias en JSON.
Permite sobrescribir el layout por defecto con posiciones personalizadas.
"""
import json
from app.utils.config import LAYOUTS_DIR
from app.pdf.templates import DEFAULT_LAYOUTS


def get_layout(table: str) -> dict:
    """Retorna el layout guardado o el layout por defecto."""
    path = LAYOUTS_DIR / f"{table}.json"
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {k: dict(v) for k, v in DEFAULT_LAYOUTS.get(table, {}).items()}


def save_layout(table: str, layout: dict):
    path = LAYOUTS_DIR / f"{table}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)


def reset_layout(table: str):
    path = LAYOUTS_DIR / f"{table}.json"
    if path.exists():
        path.unlink()
