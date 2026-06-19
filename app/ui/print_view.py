"""
Vista de impresión con editor visual de posición de campos.
Panel izquierdo: preview de la constancia (canvas tkinter, escalado).
Panel derecho: tabla de coordenadas X/Y editables.
Drag-and-drop: arrastra un campo en el preview para reposicionarlo.
"""
import tkinter as tk
import customtkinter as ctk
from app.pdf.layout_editor import get_layout, save_layout, reset_layout
from app.pdf.renderer import generate_pdf, _open_pdf, _resolve_field, PAGE_W, PAGE_H
from app.core.database import db
from pathlib import Path
import tempfile

# Escala del preview (página carta 612×792 pt → canvas ~420×545 px)
SCALE = 0.686
CANVAS_W = int(PAGE_W * SCALE)
CANVAS_H = int(PAGE_H * SCALE)
OFFSET_X = 10
OFFSET_Y = 10

# Colores del canvas
COLOR_PAGE      = "#ffffff"
COLOR_BORDER    = "#4a4a8a"
COLOR_FIELD     = "#1a237e"
COLOR_FIELD_SEL = "#e53935"
COLOR_LABEL     = "#555555"
COLOR_VALUE     = "#1a1a1a"


def _pt_to_canvas(x_pt: float, y_pt: float):
    """Convierte coordenadas PDF (origen abajo-izquierda) a canvas (origen arriba-izquierda)."""
    cx = x_pt * SCALE + OFFSET_X
    cy = (PAGE_H - y_pt) * SCALE + OFFSET_Y
    return cx, cy


def _canvas_to_pt(cx: float, cy: float):
    """Convierte coordenadas canvas a coordenadas PDF."""
    x_pt = (cx - OFFSET_X) / SCALE
    y_pt = PAGE_H - (cy - OFFSET_Y) / SCALE
    return round(x_pt, 1), round(y_pt, 1)


class PrintView(ctk.CTkToplevel):
    def __init__(self, parent, table: str, row_id: int):
        super().__init__(parent)
        self.table = table
        self.row_id = row_id
        self._layout: dict = get_layout(table)
        self._data: dict = self._load_data()
        self._selected_key: str | None = None
        self._drag_start = None

        titulo = self._data.get("nombre") or self._data.get("pareja") or f"#{row_id}"
        self.title(f"Constancia — {titulo}")
        self.geometry(f"{CANVAS_W + 360 + 40}x{CANVAS_H + 60}")
        self.resizable(False, False)
        self.grab_set()

        self._build()
        self._draw_preview()

    # ------------------------------------------------------------------
    def _load_data(self) -> dict:
        with db() as conn:
            row = conn.execute(f"SELECT * FROM {self.table} WHERE id=?", (self.row_id,)).fetchone()
        return dict(row) if row else {}

    # ------------------------------------------------------------------
    def _build(self):
        main = ctk.CTkFrame(self, fg_color="#1a1a2e")
        main.pack(fill="both", expand=True, padx=8, pady=8)

        # ── Panel izquierdo: canvas ──
        left = ctk.CTkFrame(main, fg_color="#0a0a1a",
                            width=CANVAS_W + OFFSET_X * 2,
                            height=CANVAS_H + OFFSET_Y * 2)
        left.pack(side="left", padx=(0, 8), fill="y")
        left.pack_propagate(False)

        self._canvas = tk.Canvas(
            left,
            width=CANVAS_W + OFFSET_X * 2,
            height=CANVAS_H + OFFSET_Y * 2,
            bg="#0a0a1a", highlightthickness=0,
        )
        self._canvas.pack()
        self._canvas.bind("<ButtonPress-1>",   self._on_press)
        self._canvas.bind("<B1-Motion>",        self._on_drag)
        self._canvas.bind("<ButtonRelease-1>",  self._on_release)

        # ── Panel derecho: controles ──
        right = ctk.CTkFrame(main, fg_color="transparent", width=340)
        right.pack(side="left", fill="both", expand=True)
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Posición de campos",
                     font=("Roboto", 14, "bold")).pack(pady=(4, 8))

        # Tabla de campos
        self._fields_frame = ctk.CTkScrollableFrame(right, height=380)
        self._fields_frame.pack(fill="x", padx=4)

        self._coord_entries: dict[str, tuple] = {}  # key → (x_var, y_var, size_var)
        self._build_fields_table()

        # Botones
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=4, pady=(12, 4))

        ctk.CTkButton(btn_frame, text="Imprimir constancia",
                      fg_color="#4ade80", text_color="black",
                      command=self._print).pack(fill="x", pady=2)
        ctk.CTkButton(btn_frame, text="Guardar posiciones",
                      fg_color="#60a5fa", text_color="black",
                      command=self._save_layout).pack(fill="x", pady=2)
        ctk.CTkButton(btn_frame, text="Restablecer posiciones por defecto",
                      fg_color="transparent", border_width=1,
                      command=self._reset_layout).pack(fill="x", pady=2)
        ctk.CTkButton(btn_frame, text="Cerrar",
                      fg_color="transparent", border_width=1,
                      command=self.destroy).pack(fill="x", pady=2)

        ctk.CTkLabel(right,
                     text="Arrastra los campos en el preview\no edita las coordenadas directamente.",
                     font=("Roboto", 10), text_color="gray").pack(pady=(8, 0))

    def _build_fields_table(self):
        for w in self._fields_frame.winfo_children():
            w.destroy()
        self._coord_entries.clear()

        # Encabezado
        hdr = ctk.CTkFrame(self._fields_frame, fg_color="#1a1a2e")
        hdr.pack(fill="x", pady=(0, 2))
        for text, w in [("Campo", 110), ("X", 60), ("Y", 60), ("Tam.", 50)]:
            ctk.CTkLabel(hdr, text=text, width=w, font=("Roboto", 10, "bold"),
                         anchor="w").pack(side="left", padx=2)

        for key, fdef in self._layout.items():
            row = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            label_text = fdef.get("label", key)[:14]
            lbl = ctk.CTkLabel(row, text=label_text, width=110, anchor="w",
                               font=("Roboto", 10), cursor="hand2")
            lbl.pack(side="left", padx=2)
            lbl.bind("<Button-1>", lambda e, k=key: self._select_field(k))

            x_var = ctk.StringVar(value=str(fdef.get("x", 80)))
            y_var = ctk.StringVar(value=str(fdef.get("y", 400)))
            s_var = ctk.StringVar(value=str(fdef.get("font_size", 12)))

            for var, w in [(x_var, 60), (y_var, 60), (s_var, 50)]:
                e = ctk.CTkEntry(row, textvariable=var, width=w, font=("Roboto", 10))
                e.pack(side="left", padx=2)
                var.trace_add("write", lambda *_, k=key: self._on_entry_change(k))

            self._coord_entries[key] = (x_var, y_var, s_var)

    def _on_entry_change(self, key: str):
        """Actualiza el layout y redibuja cuando el usuario edita una coordenada."""
        if key not in self._coord_entries:
            return
        x_var, y_var, s_var = self._coord_entries[key]
        try:
            x = float(x_var.get())
            y = float(y_var.get())
            s = int(s_var.get())
            self._layout[key]["x"] = x
            self._layout[key]["y"] = y
            self._layout[key]["font_size"] = s
            self._draw_preview()
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Preview canvas
    # ------------------------------------------------------------------
    def _draw_preview(self):
        self._canvas.delete("all")

        # Fondo de página
        px1, py1 = OFFSET_X, OFFSET_Y
        px2 = px1 + CANVAS_W
        py2 = py1 + CANVAS_H
        self._canvas.create_rectangle(px1, py1, px2, py2,
                                      fill=COLOR_PAGE, outline=COLOR_BORDER, width=2)
        # Borde interior
        self._canvas.create_rectangle(px1 + 4, py1 + 4, px2 - 4, py2 - 4,
                                      fill="", outline=COLOR_BORDER, width=0.5)

        # Pie de página
        foot_y = py2 - 12
        self._canvas.create_text(
            px1 + CANVAS_W // 2, foot_y,
            text="Parroquia — Sistema NSDP",
            font=("Helvetica", 7), fill="#888888", anchor="center",
        )

        # Campos
        for key, fdef in self._layout.items():
            cx, cy = _pt_to_canvas(fdef.get("x", 80), fdef.get("y", 400))
            font_size = max(6, int(fdef.get("font_size", 12) * SCALE))
            bold = fdef.get("bold", False)
            center = fdef.get("center", False)
            label = fdef.get("label", "")
            field_key = fdef.get("field")

            is_selected = (key == self._selected_key)
            color = COLOR_FIELD_SEL if is_selected else COLOR_FIELD
            font_style = ("Helvetica", font_size, "bold") if bold else ("Helvetica", font_size)
            anchor = "center" if center else "w"

            if field_key is None:
                text = label
            else:
                value = _resolve_field(field_key, self._data)
                text = f"{label} {value}".strip() if center else label

            item = self._canvas.create_text(
                cx, cy, text=text, font=font_style,
                fill=color, anchor=anchor, tags=(key, "field"),
            )

            # Valor debajo del label (si no es centrado)
            if field_key and not center:
                value = _resolve_field(field_key, self._data)
                if value:
                    lw = len(label) * font_size * 0.55 + 4
                    self._canvas.create_text(
                        cx + lw, cy, text=value,
                        font=("Helvetica", font_size),
                        fill=COLOR_VALUE, anchor="w",
                        tags=(key + "_val", "field_val"),
                    )

            # Indicador de selección
            if is_selected:
                bbox = self._canvas.bbox(item)
                if bbox:
                    self._canvas.create_rectangle(
                        bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2,
                        outline=COLOR_FIELD_SEL, fill="", width=1,
                        tags=(key + "_sel",),
                    )

    # ------------------------------------------------------------------
    # Drag-and-drop
    # ------------------------------------------------------------------
    def _on_press(self, event):
        items = self._canvas.find_overlapping(
            event.x - 10, event.y - 10, event.x + 10, event.y + 10
        )
        for item in reversed(items):
            tags = self._canvas.gettags(item)
            if "field" in tags and len(tags) >= 1:
                key = tags[0]
                if key in self._layout:
                    self._select_field(key)
                    self._drag_start = (event.x, event.y,
                                        self._layout[key]["x"],
                                        self._layout[key]["y"])
                    return
        self._drag_start = None

    def _on_drag(self, event):
        if self._drag_start is None or self._selected_key is None:
            return
        sx, sy, ox, oy = self._drag_start
        dx = (event.x - sx) / SCALE
        dy = -(event.y - sy) / SCALE   # invertir eje Y
        new_x = round(ox + dx, 1)
        new_y = round(oy + dy, 1)
        self._layout[self._selected_key]["x"] = new_x
        self._layout[self._selected_key]["y"] = new_y
        self._sync_entries(self._selected_key)
        self._draw_preview()

    def _on_release(self, event):
        self._drag_start = None

    def _select_field(self, key: str):
        self._selected_key = key
        self._draw_preview()

    def _sync_entries(self, key: str):
        """Actualiza las entradas de coordenadas sin disparar trace."""
        if key not in self._coord_entries:
            return
        x_var, y_var, _ = self._coord_entries[key]
        fdef = self._layout[key]
        x_var.set(str(fdef.get("x", 0)))
        y_var.set(str(fdef.get("y", 0)))

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _save_layout(self):
        save_layout(self.table, self._layout)
        ctk.CTkMessagebox = None  # no disponible siempre
        lbl = ctk.CTkLabel(self, text="Layout guardado.", text_color="#4ade80",
                           font=("Roboto", 11))
        lbl.place(relx=0.5, rely=0.97, anchor="center")
        self.after(2000, lbl.destroy)

    def _reset_layout(self):
        reset_layout(self.table)
        from app.pdf.templates import DEFAULT_LAYOUTS
        self._layout = {k: dict(v) for k, v in DEFAULT_LAYOUTS.get(self.table, {}).items()}
        self._build_fields_table()
        self._draw_preview()

    def _print(self):
        tmp = Path(tempfile.gettempdir()) / "nsdp_constancias"
        tmp.mkdir(exist_ok=True)
        nombre = self._data.get("nombre") or self._data.get("pareja") or str(self.row_id)
        nombre_safe = "".join(c for c in nombre if c.isalnum() or c in " _-")[:40]
        out = tmp / f"{self.table}_{nombre_safe}_{self.row_id}.pdf"
        generate_pdf(self.table, self._data, out)
        _open_pdf(out)
