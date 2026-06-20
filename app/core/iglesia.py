import json
from app.utils.config import IGLESIA_JSON

DEFAULTS: dict = {
    "nombre":          "Parroquia Nuestra Señora de la Paz",
    "ciudad":          "Hermosillo, Sonora",
    "direccion":       "",
    "codigo_postal":   "",
    "parroco_actual":  "",
    "telefono":        "",
    "horario_oficina": "",
    "secretaria":      "",
    "email":           "",
    "facebook":        "",
    "instagram":       "",
    "logo_file":       None,
    "foto_file":       None,
}


def load() -> dict:
    """Devuelve los ajustes de la iglesia, fusionados con los defaults."""
    if not IGLESIA_JSON.exists():
        return DEFAULTS.copy()
    try:
        with open(IGLESIA_JSON, encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULTS, **data}
    except Exception:
        return DEFAULTS.copy()


def save(data: dict) -> None:
    """Persiste los ajustes en iglesia.json."""
    with open(IGLESIA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
