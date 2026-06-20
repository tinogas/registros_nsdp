"""
Genera constancias en PDF usando ReportLab Canvas.
Las coordenadas se leen del layout JSON (personalizable).
"""
import os
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.database import db
from app.pdf.layout_editor import get_layout
from app.utils.config import ASSETS_DIR

PAGE_W, PAGE_H = LETTER   # 612 x 792 pt


def _resolve_field(field_key: str, data: dict) -> str:
    """Convierte claves compuestas (_fecha, _padres, etc.) en texto listo para imprimir."""
    if field_key is None:
        return ""

    if not field_key.startswith("_"):
        return str(data.get(field_key) or "")

    # Fechas compuestas
    if field_key == "_fecha":
        dia = data.get("dia") or ""
        mes = data.get("mes") or ""
        anio = data.get("anio") or ""
        return f"{dia} de {mes} de {anio}".strip(" de")

    if field_key == "_fecha_nacimiento":
        dia = data.get("dia_nacimiento") or ""
        mes = data.get("mes_nacimiento") or ""
        anio = data.get("anio_nacimiento") or ""
        return f"{dia} de {mes} de {anio}".strip(" de")

    if field_key == "_fecha_bautismo":
        dia = data.get("dia_bautismo") or ""
        mes = data.get("mes_bautismo") or ""
        anio = data.get("anio_bautismo") or ""
        return f"{dia} de {mes} de {anio}".strip(" de")

    # Padres
    if field_key in ("_padres", "_padres_comunion", "_padres_catecumeno"):
        papa_key = "papa" if "_catecumeno" not in field_key else "padre"
        mama_key = "mama" if "_catecumeno" not in field_key else "madre"
        papa = data.get(papa_key) or ""
        mama = data.get(mama_key) or ""
        parts = [p for p in [papa, mama] if p]
        return " y ".join(parts)

    if field_key == "_testigos":
        t = [data.get(f"testigo{i}") or "" for i in range(1, 5)]
        return ", ".join(x for x in t if x)

    if field_key == "_padrinos_bautismo":
        p = data.get("padrino") or ""
        m = data.get("madrina") or ""
        parts = [x for x in [p, m] if x]
        return " y ".join(parts)

    if field_key == "_registro":
        libro = data.get("libro") or ""
        pag = data.get("pagina") or ""
        partida = data.get("partida") or ""
        parts = []
        if libro:
            parts.append(f"Libro {libro}")
        if pag:
            parts.append(f"Pág. {pag}")
        if partida:
            parts.append(f"Partida {partida}")
        return ", ".join(parts)

    if field_key == "_registro_bautismo":
        reg = data.get("registro_no") or ""
        libro = data.get("libro") or ""
        pag = data.get("pagina") or ""
        acta = data.get("acta") or ""
        parts = []
        if reg:
            parts.append(f"No. {reg}")
        if libro:
            parts.append(f"Libro {libro}")
        if pag:
            parts.append(f"Pág. {pag}")
        if acta:
            parts.append(f"Acta {acta}")
        return ", ".join(parts)

    return ""


def _draw_layout(c: canvas.Canvas, layout: dict, data: dict):
    for key, field_def in layout.items():
        x = field_def.get("x", 80)
        y = field_def.get("y", 400)
        font_size = field_def.get("font_size", 12)
        bold = field_def.get("bold", False)
        center = field_def.get("center", False)
        label = field_def.get("label", "")
        field_key = field_def.get("field")

        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, font_size)
        c.setFillColor(colors.black)

        if field_key is None:
            # Texto fijo (título, encabezado)
            if center:
                c.drawCentredString(x, y, label)
            else:
                c.drawString(x, y, label)
        else:
            value = _resolve_field(field_key, data)
            if center:
                c.drawCentredString(x, y, f"{label} {value}".strip())
            else:
                c.setFont("Helvetica-Bold", font_size)
                c.drawString(x, y, label)
                c.setFont("Helvetica", font_size)
                label_w = c.stringWidth(label, "Helvetica-Bold", font_size)
                c.drawString(x + label_w + 6, y, value)


def _draw_border(c: canvas.Canvas):
    c.setStrokeColor(colors.HexColor("#4a4a8a"))
    c.setLineWidth(2)
    c.rect(36, 36, PAGE_W - 72, PAGE_H - 72)
    c.setLineWidth(0.5)
    c.rect(42, 42, PAGE_W - 84, PAGE_H - 84)


def _draw_logo(c: canvas.Canvas):
    logo_path = ASSETS_DIR / "logo_parroquia.png"
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 50, PAGE_H - 120, width=80, height=80,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass


def generate_pdf(table: str, data: dict, output_path: Path) -> Path:
    layout = get_layout(table)
    c = canvas.Canvas(str(output_path), pagesize=LETTER)
    _draw_border(c)
    _draw_logo(c)

    # Pie de página
    from app.core.iglesia import load as _load_iglesia
    _cfg = _load_iglesia()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawCentredString(PAGE_W / 2, 50,
                        f"{_cfg['nombre']} — Documento oficial")

    _draw_layout(c, layout, data)
    c.save()
    return output_path


def generate_constancia(table: str, row_id: int) -> Path:
    with db() as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()
    if not row:
        raise ValueError(f"Registro {row_id} no encontrado en {table}")

    data = dict(row)
    tmp_dir = Path(tempfile.gettempdir()) / "nsdp_constancias"
    tmp_dir.mkdir(exist_ok=True)

    nombre = data.get("nombre") or data.get("pareja") or str(row_id)
    nombre_safe = "".join(c for c in nombre if c.isalnum() or c in " _-")[:40]
    output_path = tmp_dir / f"{table}_{nombre_safe}_{row_id}.pdf"

    generate_pdf(table, data, output_path)
    _open_pdf(output_path)
    return output_path


def _open_pdf(path: Path):
    try:
        import win32api
        win32api.ShellExecute(0, "open", str(path), None, ".", 1)
    except Exception:
        os.startfile(str(path))


# ── Modo formulario pre-impreso ───────────────────────────────────────────────

def _draw_form_fields(c: canvas.Canvas, fields: dict, data: dict, page_w: float, page_h: float):
    """Dibuja solo los valores (sin etiquetas ni decoración) sobre un formulario físico."""
    for _key, fdef in fields.items():
        field_key = fdef.get("field")
        if not field_key:
            continue
        value = _resolve_field(field_key, data)
        if not value:
            continue
        x = fdef.get("x", 80)
        y = fdef.get("y", 300)
        font_size = fdef.get("font_size", 11)
        center = fdef.get("center", False)
        c.setFont("Helvetica", font_size)
        c.setFillColor(colors.black)
        if center:
            c.drawCentredString(page_w / 2, y, value)
        else:
            c.drawString(x, y, value)


def generate_form_pdf(table: str, data: dict, output_path: Path,
                      form_layout: dict | None = None) -> Path:
    """Genera PDF con solo los datos del registro para imprimir sobre un formulario pre-impreso.

    form_layout: dict con claves 'page_size' y 'fields'. Si es None, se carga del JSON guardado.
    """
    from app.pdf.layout_editor import get_form_layout
    form = form_layout if form_layout is not None else get_form_layout(table)
    page_size = tuple(form.get("page_size", list(LETTER)))
    c = canvas.Canvas(str(output_path), pagesize=page_size)
    _draw_form_fields(c, form.get("fields", {}), data, page_size[0], page_size[1])
    c.save()
    return output_path


def generate_form_constancia(table: str, row_id: int) -> Path:
    """Versión de generate_constancia para modo formulario."""
    with db() as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()
    if not row:
        raise ValueError(f"Registro {row_id} no encontrado en {table}")
    data = dict(row)
    tmp_dir = Path(tempfile.gettempdir()) / "nsdp_constancias"
    tmp_dir.mkdir(exist_ok=True)
    nombre = data.get("nombre") or data.get("pareja") or str(row_id)
    nombre_safe = "".join(ch for ch in nombre if ch.isalnum() or ch in " _-")[:40]
    output_path = tmp_dir / f"{table}_forma_{nombre_safe}_{row_id}.pdf"
    generate_form_pdf(table, data, output_path)
    _open_pdf(output_path)
    return output_path
