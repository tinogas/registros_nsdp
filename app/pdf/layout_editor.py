"""
Persistencia de layouts de constancias en JSON.
Permite sobrescribir el layout por defecto con posiciones personalizadas.
"""
import json
from app.utils.config import LAYOUTS_DIR
from app.pdf.templates import DEFAULT_LAYOUTS


_PAGE_H = 612.0  # media carta vertical; layouts con y > este valor son obsoletos

def get_layout(table: str) -> dict:
    """Retorna el layout guardado o el layout por defecto.
    Descarta layouts diseñados para carta completa (y > 612)."""
    path = LAYOUTS_DIR / f"{table}.json"
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                stored = json.load(f)
            max_y = max((v.get("y", 0) for v in stored.values()), default=0)
            if max_y <= _PAGE_H:
                return stored
            path.unlink()  # layout obsoleto (tamaño carta completa)
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


# ── Layouts de formularios pre-impresos ──────────────────────────────────────

def get_form_layout(table: str) -> dict:
    """Retorna el layout de formulario guardado o el default de FORM_LAYOUTS.
    Descarta el JSON guardado si su page_size no coincide con el default actual."""
    from app.pdf.templates import FORM_LAYOUTS
    raw = FORM_LAYOUTS.get(table, {})
    default_size = list(raw.get("page_size", [612, 792]))
    default_fields = {k: dict(v) for k, v in raw.get("fields", {}).items()}

    path = LAYOUTS_DIR / f"{table}_forma.json"
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                stored = json.load(f)
            if list(stored.get("page_size", [])) == default_size:
                return stored
            path.unlink()  # page_size cambió — descartar calibración obsoleta
        except Exception:
            pass
    return {"page_size": default_size, "fields": default_fields}


def save_form_layout(table: str, layout: dict):
    path = LAYOUTS_DIR / f"{table}_forma.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)


def reset_form_layout(table: str):
    path = LAYOUTS_DIR / f"{table}_forma.json"
    if path.exists():
        path.unlink()
