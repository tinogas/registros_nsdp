"""
Vista de impresión con editor visual de posición de campos.
Panel izquierdo: preview de la constancia (canvas tkinter, escalado).
Panel derecho: tabla de coordenadas X/Y editables.
Drag-and-drop: arrastra un campo en el preview para reposicionarlo.

form_mode=True: muestra el formulario pre-impreso como fondo y genera
PDF con solo los datos (sin borde/logo/pie), para imprimir sobre el papel físico.
"""
import tkinter as tk
import customtkinter as ctk
from app.pdf.layout_editor import (
    get_layout, save_layout, reset_layout,
    get_form_layout, save_form_layout, reset_form_layout,
)
from app.pdf.renderer import (
    generate_pdf, generate_form_pdf, print_pdf, _resolve_field,
    PAGE_W, PAGE_H,
)
from app.core.database import db
from app.utils.config import BUNDLE_DIR
from pathlib import Path
import tempfile

# Dimensiones máximas del canvas de preview
_MAX_CANVAS_W = 500
_MAX_CANVAS_H = 545
_OFFSET_X = 10
_OFFSET_Y = 10

# Imágenes de referencia por tabla (en la raíz del proyecto)
_FORM_IMAGES = {
    "bautismos":       "Formato_Bautizo.jpg",
    "primera_comunion":"Formato_1ra_Comunion.jpg",
    "confirmacion":    "Formato_confirmacion.jpg",
    "matrimonios":     "Formato_matrimonio.jpg",
}

# Colores del canvas
COLOR_PAGE      = "#ffffff"
COLOR_BORDER    = "#4a4a8a"
COLOR_FIELD     = "#1a237e"
COLOR_FIELD_SEL = "#e53935"
COLOR_LABEL     = "#555555"
COLOR_VALUE     = "#1a1a1a"


def _compute_scale(pw: float, ph: float) -> float:
    sw = _MAX_CANVAS_W / pw
    sh = _MAX_CANVAS_H / ph
    return min(sw, sh)


def _pt_to_canvas(x_pt: float, y_pt: float, scale: float, ph: float):
    cx = x_pt * scale + _OFFSET_X
    cy = (ph - y_pt) * scale + _OFFSET_Y
    return cx, cy


def _canvas_to_pt(cx: float, cy: float, scale: float, ph: float):
    x_pt = (cx - _OFFSET_X) / scale
    y_pt = ph - (cy - _OFFSET_Y) / scale
    return round(x_pt, 1), round(y_pt, 1)


class PrintView(ctk.CTkToplevel):
    def __init__(self, parent, table: str, row_id: int, form_mode: bool = False):
        super().__init__(parent)
        self.table = table
        self.row_id = row_id
        self.form_mode = form_mode
        self._data: dict = self._load_data()
        self._selected_key: str | None = None
        self._drag_start = None
        self._bg_photo = None   # referencia para PIL PhotoImage
        self._show_bg = True    # True = mostrar imagen guía de fondo
        self._updating_entries = False  # guard: evita que el trace de _sync_entries resetee coordenadas
        self._zoom_factor = 1.0

        self._reload_layout()   # carga _layout, _pw, _ph, _scale, _base_scale, _canvas_w, _canvas_h

        titulo = self._data.get("nombre") or self._data.get("pareja") or f"#{row_id}"
        modo = "Formulario — " if form_mode else "Constancia — "
        self.title(f"{modo}{titulo}")
        win_h = max(self._canvas_h + 80, 660)
        self.geometry(f"{self._canvas_w + 360 + 40}x{win_h}")
        self.resizable(True, True)
        self.grab_set()

        self._build()
        self._draw_preview()

    # ------------------------------------------------------------------
    def _load_data(self) -> dict:
        with db() as conn:
            row = conn.execute(f"SELECT * FROM {self.table} WHERE id=?", (self.row_id,)).fetchone()
        return dict(row) if row else {}

    def _reload_layout(self):
        if self.form_mode:
            form = get_form_layout(self.table)
            self._pw = float(form["page_size"][0])
            self._ph = float(form["page_size"][1])
            fs = form.get("form_size", form["page_size"])
            self._form_w = float(fs[0])
            self._form_h = float(fs[1])
            self._layout = form["fields"]
        else:
            self._pw = float(PAGE_W)
            self._ph = float(PAGE_H)
            self._form_w = self._pw
            self._form_h = self._ph
            self._layout = get_layout(self.table)

        self._base_scale = _compute_scale(self._pw, self._ph)
        self._scale = self._base_scale * self._zoom_factor
        self._canvas_w = int(self._pw * self._scale)
        self._canvas_h = int(self._ph * self._scale)

    # ------------------------------------------------------------------
    def _build(self):
        main = ctk.CTkFrame(self, fg_color="#1a1a2e")
        main.pack(fill="both", expand=True, padx=8, pady=8)

        # ── Panel izquierdo: canvas ──
        left = ctk.CTkFrame(main, fg_color="#0a0a1a",
                            width=self._canvas_w + _OFFSET_X * 2,
                            height=self._canvas_h + _OFFSET_Y * 2)
        left.pack(side="left", padx=(0, 8), fill="y")
        left.pack_propagate(False)
        self._left_frame = left

        self._canvas = tk.Canvas(
            left,
            width=self._canvas_w + _OFFSET_X * 2,
            height=self._canvas_h + _OFFSET_Y * 2,
            bg="#0a0a1a", highlightthickness=0,
        )
        self._canvas.pack()
        self._canvas.bind("<ButtonPress-1>",   self._on_press)
        self._canvas.bind("<B1-Motion>",        self._on_drag)
        self._canvas.bind("<ButtonRelease-1>",  self._on_release)

        # Barra de zoom
        zoom_bar = ctk.CTkFrame(left, fg_color="transparent")
        zoom_bar.pack(fill="x", padx=4, pady=(2, 0))
        ctk.CTkButton(zoom_bar, text="−", width=28, height=24,
                      fg_color="#2d3748", hover_color="#374151",
                      command=self._zoom_out).pack(side="left", padx=2)
        ctk.CTkButton(zoom_bar, text="+", width=28, height=24,
                      fg_color="#2d3748", hover_color="#374151",
                      command=self._zoom_in).pack(side="left", padx=2)
        ctk.CTkButton(zoom_bar, text="Ajustar", width=60, height=24,
                      fg_color="#2d3748", hover_color="#374151",
                      command=self._zoom_fit).pack(side="left", padx=2)
        self._zoom_label = ctk.CTkLabel(zoom_bar, text="Ajustar",
                                        font=("Roboto", 10), text_color="#a0aec0")
        self._zoom_label.pack(side="left", padx=4)

        # ── Panel derecho: controles ──
        right = ctk.CTkFrame(main, fg_color="transparent", width=340)
        right.pack(side="left", fill="both", expand=True)
        right.pack_propagate(False)

        header = "Posición de campos — Formulario" if self.form_mode else "Posición de campos"
        ctk.CTkLabel(right, text=header,
                     font=("Roboto", 14, "bold")).pack(pady=(4, 8))

        # Tabla de campos
        self._fields_frame = ctk.CTkScrollableFrame(right, height=380)
        self._fields_frame.pack(fill="x", padx=4)

        self._coord_entries: dict[str, tuple] = {}
        self._build_fields_table()

        # Botones
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=4, pady=(12, 4))

        if self.form_mode:
            ctk.CTkButton(btn_frame, text="Imprimir en formulario",
                          fg_color="#f97316", text_color="black",
                          command=self._print).pack(fill="x", pady=2)
            ctk.CTkButton(btn_frame, text="Guardar posiciones",
                          fg_color="#60a5fa", text_color="black",
                          command=self._save_layout).pack(fill="x", pady=2)
            ctk.CTkButton(btn_frame, text="Restablecer posiciones",
                          fg_color="transparent", border_width=1,
                          command=self._reset_layout).pack(fill="x", pady=2)
            self._btn_toggle_bg = ctk.CTkButton(
                btn_frame, text="Ocultar guía (solo campos)",
                fg_color="#7c3aed", text_color="white",
                command=self._toggle_bg,
            )
            self._btn_toggle_bg.pack(fill="x", pady=2)
        else:
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

        hint = ("Arrastra los campos sobre el formulario\no edita las coordenadas directamente."
                if self.form_mode else
                "Arrastra los campos en el preview\no edita las coordenadas directamente.")
        ctk.CTkLabel(right, text=hint,
                     font=("Roboto", 10), text_color="gray").pack(pady=(8, 0))

    def _build_fields_table(self):
        for w in self._fields_frame.winfo_children():
            w.destroy()
        self._coord_entries.clear()

        hdr = ctk.CTkFrame(self._fields_frame, fg_color="#1a1a2e")
        hdr.pack(fill="x", pady=(0, 2))
        for text, w in [("Campo", 110), ("X", 60), ("Y", 60), ("Tam.", 50)]:
            ctk.CTkLabel(hdr, text=text, width=w, font=("Roboto", 10, "bold"),
                         anchor="w").pack(side="left", padx=2)

        for key, fdef in self._layout.items():
            if not self.form_mode and fdef.get("field") is None:
                label_text = fdef.get("label", key)[:14]
            elif self.form_mode:
                label_text = key[:14]
            else:
                label_text = fdef.get("label", key)[:14]

            row = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            lbl = ctk.CTkLabel(row, text=label_text, width=110, anchor="w",
                               font=("Roboto", 10), cursor="hand2")
            lbl.pack(side="left", padx=2)
            lbl.bind("<Button-1>", lambda e, k=key: self._select_field(k))

            x_var = ctk.StringVar(value=str(fdef.get("x", 80)))
            y_var = ctk.StringVar(value=str(fdef.get("y", 400)))
            s_var = ctk.StringVar(value=str(fdef.get("font_size", 11 if self.form_mode else 12)))

            for var, w in [(x_var, 60), (y_var, 60), (s_var, 50)]:
                e = ctk.CTkEntry(row, textvariable=var, width=w, font=("Roboto", 10))
                e.pack(side="left", padx=2)
                var.trace_add("write", lambda *_, k=key: self._on_entry_change(k))

            self._coord_entries[key] = (x_var, y_var, s_var)

    def _on_entry_change(self, key: str):
        if self._updating_entries or key not in self._coord_entries:
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
    def _toggle_bg(self):
        """Alterna entre mostrar la imagen guía y solo los campos (vista de impresión real)."""
        self._show_bg = not self._show_bg
        if self._show_bg:
            self._btn_toggle_bg.configure(text="Ocultar guía (solo campos)")
        else:
            self._btn_toggle_bg.configure(text="Mostrar guía del formulario")
        self._draw_preview()

    def _load_bg_image(self):
        """Carga la imagen del formulario a su tamaño físico real sobre fondo blanco carta."""
        img_name = _FORM_IMAGES.get(self.table)
        if not img_name:
            return
        img_path = BUNDLE_DIR / img_name
        if not img_path.exists():
            return
        try:
            from PIL import Image, ImageTk
            img = Image.open(img_path).convert("RGB")
            # Tamaño de display exacto según las dimensiones físicas del formulario
            disp_w = max(1, int(self._form_w * self._scale))
            disp_h = max(1, int(self._form_h * self._scale))
            img = img.resize((disp_w, disp_h), Image.LANCZOS)
            # Pegar en la esquina superior izquierda de un fondo blanco carta
            bg = Image.new("RGB", (self._canvas_w, self._canvas_h), "white")
            bg.paste(img, (0, 0))
            self._bg_photo = ImageTk.PhotoImage(bg)
        except Exception:
            self._bg_photo = None

    def _draw_preview(self):
        self._canvas.delete("all")

        px1, py1 = _OFFSET_X, _OFFSET_Y
        px2 = px1 + self._canvas_w
        py2 = py1 + self._canvas_h

        if self.form_mode:
            if self._show_bg:
                # Con guía: imagen del formulario pre-impreso como fondo
                if self._bg_photo is None:
                    self._load_bg_image()
                if self._bg_photo:
                    self._canvas.create_image(px1, py1, anchor="nw", image=self._bg_photo)
                else:
                    # Sin imagen disponible: fondo blanco con indicación
                    self._canvas.create_rectangle(px1, py1, px2, py2,
                                                  fill=COLOR_PAGE, outline="#888888", width=1)
                    self._canvas.create_text(
                        px1 + self._canvas_w // 2, py1 + self._canvas_h // 2,
                        text=f"Imagen no encontrada:\n{_FORM_IMAGES.get(self.table, '')}",
                        font=("Helvetica", 9), fill="#aaaaaa", anchor="center",
                    )
            else:
                # Sin guía: hoja en blanco — muestra exactamente lo que se imprimirá
                self._canvas.create_rectangle(px1, py1, px2, py2,
                                              fill=COLOR_PAGE, outline="#cccccc", width=1)
        else:
            # Fondo: página blanca con borde decorativo
            self._canvas.create_rectangle(px1, py1, px2, py2,
                                          fill=COLOR_PAGE, outline=COLOR_BORDER, width=2)
            self._canvas.create_rectangle(px1 + 4, py1 + 4, px2 - 4, py2 - 4,
                                          fill="", outline=COLOR_BORDER, width=0.5)
            foot_y = py2 - 12
            self._canvas.create_text(
                px1 + self._canvas_w // 2, foot_y,
                text="Parroquia — Sistema NSDP",
                font=("Helvetica", 7), fill="#888888", anchor="center",
            )

        # Campos
        for key, fdef in self._layout.items():
            cx, cy = _pt_to_canvas(fdef.get("x", 80), fdef.get("y", 400),
                                   self._scale, self._ph)
            font_size = max(6, int(fdef.get("font_size", 11) * self._scale))
            bold = fdef.get("bold", False)
            center = fdef.get("center", False)
            field_key = fdef.get("field")
            label = fdef.get("label", "")

            is_selected = (key == self._selected_key)
            if is_selected:
                color = COLOR_FIELD_SEL
            elif self.form_mode and self._show_bg:
                color = "#cc0000"   # rojo intenso para ver sobre la imagen guía
            elif self.form_mode:
                color = "#111111"   # negro: vista de lo que se imprimirá realmente
            else:
                color = COLOR_FIELD
            font_style = ("Helvetica", font_size, "bold") if bold else ("Helvetica", font_size)
            anchor = "center" if center else "w"

            if self.form_mode:
                # Solo dibuja el valor (sin etiqueta) en rojo intenso para ver dónde cae
                value = _resolve_field(field_key, self._data) if field_key else ""
                display = value or f"[{key}]"
                item = self._canvas.create_text(
                    cx, cy, text=display, font=font_style,
                    fill=color, anchor=anchor, tags=(key, "field"),
                )
            else:
                if field_key is None:
                    text = label
                else:
                    value = _resolve_field(field_key, self._data)
                    text = f"{label} {value}".strip() if center else label
                item = self._canvas.create_text(
                    cx, cy, text=text, font=font_style,
                    fill=color, anchor=anchor, tags=(key, "field"),
                )
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

            if is_selected:
                bbox = self._canvas.bbox(item)
                if bbox:
                    self._canvas.create_rectangle(
                        bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2,
                        outline=COLOR_FIELD_SEL, fill="", width=1,
                        tags=(key + "_sel",),
                    )

    # ------------------------------------------------------------------
    # Zoom
    # ------------------------------------------------------------------
    def _zoom_in(self):
        self._zoom_factor = min(self._zoom_factor * 1.25, 4.0)
        self._apply_zoom()

    def _zoom_out(self):
        self._zoom_factor = max(self._zoom_factor / 1.25, 0.25)
        self._apply_zoom()

    def _zoom_fit(self):
        self._zoom_factor = 1.0
        self._apply_zoom()

    def _apply_zoom(self):
        self._scale = self._base_scale * self._zoom_factor
        self._canvas_w = int(self._pw * self._scale)
        self._canvas_h = int(self._ph * self._scale)
        new_cw = self._canvas_w + _OFFSET_X * 2
        new_ch = self._canvas_h + _OFFSET_Y * 2
        self._canvas.configure(width=new_cw, height=new_ch)
        self._left_frame.configure(width=new_cw, height=new_ch)
        self._bg_photo = None  # fuerza recarga de la imagen al nuevo tamaño
        win_w = new_cw + 360 + 40
        win_h = max(new_ch + 80, 500)
        self.geometry(f"{win_w}x{win_h}")
        if self._zoom_factor == 1.0:
            self._zoom_label.configure(text="Ajustar")
        else:
            self._zoom_label.configure(text=f"{int(self._zoom_factor * 100)}%")
        self._draw_preview()

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
        dx = (event.x - sx) / self._scale
        dy = -(event.y - sy) / self._scale
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
        if key not in self._coord_entries:
            return
        self._updating_entries = True
        x_var, y_var, _ = self._coord_entries[key]
        fdef = self._layout[key]
        x_var.set(str(fdef.get("x", 0)))
        y_var.set(str(fdef.get("y", 0)))
        self._updating_entries = False

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _save_layout(self):
        if self.form_mode:
            form = get_form_layout(self.table)
            form["fields"] = self._layout
            save_form_layout(self.table, form)
        else:
            save_layout(self.table, self._layout)
        lbl = ctk.CTkLabel(self, text="Calibración guardada." if self.form_mode else "Layout guardado.",
                           text_color="#4ade80", font=("Roboto", 11))
        lbl.place(relx=0.5, rely=0.97, anchor="center")
        self.after(2000, lbl.destroy)

    def _reset_layout(self):
        self._zoom_factor = 1.0
        if self.form_mode:
            reset_form_layout(self.table)
            form = get_form_layout(self.table)
            self._pw = float(form["page_size"][0])
            self._ph = float(form["page_size"][1])
            self._layout = form["fields"]
            self._base_scale = _compute_scale(self._pw, self._ph)
        else:
            reset_layout(self.table)
            from app.pdf.templates import DEFAULT_LAYOUTS
            self._layout = {k: dict(v) for k, v in DEFAULT_LAYOUTS.get(self.table, {}).items()}
        self._build_fields_table()
        self._apply_zoom()

    def _print(self):
        from tkinter import messagebox
        tmp = Path(tempfile.gettempdir()) / "nsdp_constancias"
        tmp.mkdir(exist_ok=True)
        nombre = self._data.get("nombre") or self._data.get("pareja") or str(self.row_id)
        nombre_safe = "".join(c for c in nombre if c.isalnum() or c in " _-")[:40]

        try:
            if self.form_mode:
                form = get_form_layout(self.table)
                form["fields"] = self._layout
                out = tmp / f"{self.table}_forma_{nombre_safe}_{self.row_id}.pdf"
                generate_form_pdf(self.table, self._data, out, form_layout=form)
            else:
                out = tmp / f"{self.table}_{nombre_safe}_{self.row_id}.pdf"
                generate_pdf(self.table, self._data, out)
        except Exception as e:
            messagebox.showerror("Error al generar PDF", str(e), parent=self)
            return

        try:
            print_pdf(out)
        except Exception as e:
            messagebox.showerror("Error de impresión", str(e), parent=self)
