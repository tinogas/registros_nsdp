"""
Genera constancias en PDF usando ReportLab Canvas.
Las coordenadas se leen del layout JSON (personalizable).
"""
import os
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.database import db
from app.pdf.layout_editor import get_layout
from app.utils.config import ASSETS_DIR

# Media carta vertical: 5.5" × 8.5" = 396 × 612 pt
PAGE_W, PAGE_H = 396.0, 612.0

_SACRAMENT_TITLES = {
    "bautismos":        "CONSTANCIA DE BAUTISMO",
    "primera_comunion": "CONSTANCIA DE PRIMERA COMUNIÓN",
    "confirmacion":     "CONSTANCIA DE CONFIRMACIÓN",
    "matrimonios":      "CONSTANCIA DE MATRIMONIO",
    "catecumenos":      "CONSTANCIA DE CATECÚMENO",
}


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

    if field_key == "_registro":
        libro = data.get("libro") or ""
        pag = data.get("pagina") or ""
        acta = data.get("acta") or ""
        parts = []
        if libro:
            parts.append(f"Libro {libro}")
        if pag:
            parts.append(f"Pág. {pag}")
        if acta:
            parts.append(f"Acta {acta}")
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


def _draw_value_wrapped(c: canvas.Canvas, x: float, y: float, text: str,
                        font: str, font_size: float, max_w: float):
    """Dibuja texto con word-wrap de hasta 2 líneas si excede max_w."""
    if not text:
        return
    line_h = int(font_size * 1.35)
    if c.stringWidth(text, font, font_size) <= max_w:
        c.drawString(x, y, text)
        return
    words = text.split()
    line1, line2 = [], []
    for word in words:
        candidate = " ".join(line1 + [word])
        if c.stringWidth(candidate, font, font_size) <= max_w:
            line1.append(word)
        else:
            line2.append(word)
    c.drawString(x, y, " ".join(line1))
    if line2:
        c.drawString(x, y - line_h, " ".join(line2))


def _draw_layout(c: canvas.Canvas, layout: dict, data: dict):
    for key, field_def in layout.items():
        # El título del sacramento se renderiza en el encabezado dinámico
        if key == "titulo" and field_def.get("field") is None:
            continue
        x = field_def.get("x", 80)
        y = field_def.get("y", 400)
        font_size = field_def.get("font_size", 12)
        bold = field_def.get("bold", False)
        center = field_def.get("center", False)
        label = field_def.get("label", "")
        field_key = field_def.get("field")

        c.setFillColor(colors.black)

        if field_key is None:
            c.setFont("Helvetica-Bold" if bold else "Helvetica", font_size)
            if center:
                c.drawCentredString(x, y, label)
            else:
                c.drawString(x, y, label)
        else:
            value = _resolve_field(field_key, data)
            if center:
                c.setFont("Helvetica-Bold" if bold else "Helvetica", font_size)
                c.drawCentredString(x, y, f"{label} {value}".strip())
            else:
                c.setFont("Helvetica", font_size)
                c.drawString(x, y, label)
                label_w = c.stringWidth(label, "Helvetica", font_size)
                val_x = x + label_w + 6
                max_w = PAGE_W - val_x - 30
                _draw_value_wrapped(c, val_x, y, value, "Helvetica", font_size, max_w)


def _draw_border(c: canvas.Canvas):
    c.setStrokeColor(colors.HexColor("#4a4a8a"))
    c.setLineWidth(2)
    c.rect(18, 18, PAGE_W - 36, PAGE_H - 36)
    c.setLineWidth(0.5)
    c.rect(23, 23, PAGE_W - 46, PAGE_H - 46)


def _draw_header(c: canvas.Canvas, cfg: dict, table: str):
    """Encabezado completo: logo, datos de la iglesia, separadores y título del sacramento."""
    # Logo
    logo_path = ASSETS_DIR / cfg.get("logo_file", "logo_parroquia.png")
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 30, PAGE_H - 88, width=55, height=55,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # Nombre de la parroquia
    nombre = cfg.get("nombre", "")
    if nombre:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#2a2a6a"))
        c.drawString(102, PAGE_H - 44, nombre)          # y ≈ 748

    # Dirección + ciudad
    ciudad = cfg.get("ciudad", "")
    direccion = cfg.get("direccion", "")
    addr = "  ·  ".join(p for p in [direccion, ciudad] if p)
    if addr:
        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#444444"))
        max_addr_w = PAGE_W - 102 - 35
        _draw_value_wrapped(c, 102, PAGE_H - 59, addr, "Helvetica", 8.5, max_addr_w)  # y ≈ 733

    # Párroco
    parroco = cfg.get("parroco_actual", "")
    if parroco:
        c.setFont("Helvetica-Oblique", 8.5)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(102, PAGE_H - 74, parroco)         # y ≈ 718

    # Separador 1 (bajo datos de iglesia)
    c.setStrokeColor(colors.HexColor("#4a4a8a"))
    c.setLineWidth(0.5)
    c.line(28, PAGE_H - 96, PAGE_W - 28, PAGE_H - 96)  # y = 696

    # Título del sacramento
    title = _SACRAMENT_TITLES.get(table, "CONSTANCIA")
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#2a2a6a"))
    c.drawCentredString(PAGE_W / 2, PAGE_H - 112, title)  # y = 680

    # Separador 2 (bajo título)
    c.setStrokeColor(colors.HexColor("#4a4a8a"))
    c.setLineWidth(0.5)
    c.line(28, PAGE_H - 126, PAGE_W - 28, PAGE_H - 126)  # y = 666


def generate_pdf(table: str, data: dict, output_path: Path,
                 layout: dict | None = None) -> Path:
    if layout is None:
        layout = get_layout(table)
    from app.core.iglesia import load as _load_iglesia
    _cfg = _load_iglesia()

    c = canvas.Canvas(str(output_path), pagesize=(PAGE_W, PAGE_H))
    _draw_border(c)
    _draw_header(c, _cfg, table)

    # Pie de página
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawCentredString(PAGE_W / 2, 32,
                        f"{_cfg.get('nombre', '')} — Documento oficial")

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


def print_pdf(path: Path) -> None:
    """Abre el diálogo de impresión del sistema forzando orientación vertical (retrato)."""
    try:
        import win32api, win32print, win32con
        try:
            pname = win32print.GetDefaultPrinter()
            ph = win32print.OpenPrinter(pname)
            try:
                pi2 = win32print.GetPrinter(ph, 2)
                dm = pi2.get("pDevMode")
                if dm is not None:
                    dm.Orientation = win32con.DMORIENT_PORTRAIT
                    dm.Fields = dm.Fields | win32con.DM_ORIENTATION
                    win32print.SetPrinter(ph, 2, pi2, 0)
            finally:
                win32print.ClosePrinter(ph)
        except Exception:
            pass
        win32api.ShellExecute(0, "print", str(path), None, ".", 1)
    except Exception:
        try:
            os.startfile(str(path))
        except Exception:
            import subprocess
            subprocess.Popen(["cmd", "/c", "start", "", str(path)], shell=False)


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
