import datetime
import tkinter as tk
import customtkinter as ctk
from app.ui.search_view import SearchView, YEAR_ORDER_COL

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SACRAMENTOS = [
    ("bautismos",        "Bautismos",     "#3b82f6"),
    ("primera_comunion", "1a Comunión",   "#10b981"),
    ("confirmacion",     "Confirmación",  "#8b5cf6"),
    ("matrimonios",      "Matrimonios",   "#f59e0b"),
    ("catecumenos",      "Catecúmenos",   "#ec4899"),
]

TAB_ACCENT = {table: color for table, _, color in SACRAMENTOS}

_BG       = "#0a0a1a"
_HEADER   = "#0d0d1f"
_TABBAR   = "#111128"
_CARD_BG  = "#16213e"
_TEXT     = "#e2e8f0"
_MUTED    = "#a0aec0"
_RED      = "#e94560"


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NSDP — Registros Sacramentales")
        self.geometry("1200x720")
        self.minsize(960, 580)

        self._current_table = None
        self._current_view  = None
        self._build()
        self._show_dashboard()

    def _build(self):
        # ── Cabecera ───────────────────────────────────────────────────
        header = ctk.CTkFrame(self, corner_radius=0, fg_color=_HEADER, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="NSDP — Registros Sacramentales",
                     font=("Roboto", 16, "bold"),
                     text_color=_RED).pack(side="left", padx=20)

        ctk.CTkButton(
            header, text="Reportes", width=90,
            fg_color="transparent", border_width=1, border_color="gray40",
            hover_color="#1e1e3a", text_color=_MUTED,
            command=self._open_reports,
        ).pack(side="right", padx=(0, 6), pady=10)

        self._gear_btn = ctk.CTkButton(
            header, text="⚙", width=36,
            fg_color="transparent", border_width=1, border_color="gray40",
            hover_color="#1e1e3a", text_color=_MUTED,
            font=("Segoe UI", 14),
            command=self._toggle_gear_menu,
        )
        self._gear_btn.pack(side="right", padx=(0, 4), pady=10)

        # ── Barra de pestañas ──────────────────────────────────────────
        self._tabbar = ctk.CTkFrame(self, corner_radius=0, fg_color=_TABBAR, height=44)
        self._tabbar.pack(fill="x")
        self._tabbar.pack_propagate(False)

        self._tab_buttons: dict[str, ctk.CTkButton] = {}

        btn_inicio = ctk.CTkButton(
            self._tabbar, text="Inicio", width=90,
            corner_radius=0, height=44,
            fg_color=_RED, text_color="white", hover_color="#c73652",
            command=self._show_dashboard,
        )
        btn_inicio.pack(side="left")
        self._tab_buttons["__dashboard__"] = btn_inicio

        for table, label, color in SACRAMENTOS:
            btn = ctk.CTkButton(
                self._tabbar, text=label, width=120,
                corner_radius=0, height=44,
                fg_color="transparent", text_color=_MUTED, hover_color="#1e2a4a",
                command=lambda t=table: self._show_table(t),
            )
            btn.pack(side="left")
            self._tab_buttons[table] = btn

        # ── Área de contenido ──────────────────────────────────────────
        self._main = ctk.CTkFrame(self, corner_radius=0, fg_color=_BG)
        self._main.pack(fill="both", expand=True)

    # ── Navegación ─────────────────────────────────────────────────────
    def _activate_tab(self, key: str):
        for k, btn in self._tab_buttons.items():
            if k == key:
                color = _RED if k == "__dashboard__" else TAB_ACCENT.get(k, "#1e40af")
                btn.configure(fg_color=color, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=_MUTED)

    def _clear_main(self):
        if self._current_view:
            self._current_view.destroy()
            self._current_view = None

    def _show_dashboard(self):
        self._activate_tab("__dashboard__")
        self._clear_main()
        self._current_view = DashboardView(
            self._main, on_navigate=self._show_table, fg_color="transparent"
        )
        self._current_view.pack(fill="both", expand=True)

    def _show_table(self, table: str):
        self._current_table = table
        self._activate_tab(table)
        self._clear_main()
        self._current_view = SearchView(
            self._main, table=table,
            on_select=self._on_record_select,
            fg_color="transparent",
        )
        self._current_view.pack(fill="both", expand=True)

    def _on_record_select(self, table: str, row_id: int):
        from app.core.database import db
        with db() as conn:
            row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()
        if row:
            _show_detail_popup(self, table, dict(row))

    def _open_reports(self):
        from app.ui.report_view import ReportView
        ReportView(self)

    def _toggle_gear_menu(self):
        menu = tk.Menu(self, tearoff=0,
                       bg="#1a1a2e", fg="#e2e8f0",
                       activebackground="#1e40af", activeforeground="#ffffff",
                       font=("Segoe UI", 10), bd=1)
        menu.add_command(label="  ⚙  Datos de la Parroquia  ",
                         command=self._open_settings)
        menu.add_separator()
        menu.add_command(label="  📥  Importar Excel  ",
                         command=self._open_import)
        menu.add_separator()
        menu.add_command(label="  💾  Respaldos y Restauración  ",
                         command=self._open_backup)
        x = self._gear_btn.winfo_rootx()
        y = self._gear_btn.winfo_rooty() + self._gear_btn.winfo_height()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _open_settings(self):
        from app.ui.settings_view import IglesiaSettingsDialog
        def _on_saved():
            if isinstance(self._current_view, DashboardView):
                self._current_view.refresh_iglesia()
        IglesiaSettingsDialog(self, on_saved=_on_saved)

    def _open_backup(self):
        from app.ui.backup_view import BackupView
        BackupView(self)

    def _open_import(self):
        from app.ui.import_view import ImportDialog
        ImportDialog(self)


# ── Vista de inicio con KPIs ───────────────────────────────────────────────

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_navigate=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_navigate = on_navigate
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Resumen general",
                     font=("Roboto", 20, "bold"), text_color=_TEXT).pack(pady=(24, 6))

        self._iglesia_panel = _IglesiaPanel(scroll, fg_color="transparent")
        self._iglesia_panel.pack(fill="x", padx=30, pady=(0, 16))

        kpis = self._load_kpis()

        cards = ctk.CTkFrame(scroll, fg_color="transparent")
        cards.pack(fill="x", padx=30, pady=(0, 20))

        for i, (table, label, color) in enumerate(SACRAMENTOS):
            total, este_anio = kpis.get(table, (0, 0))
            card = _KpiCard(cards, label=label, total=total, este_anio=este_anio,
                            color=color,
                            on_click=lambda t=table: self._on_navigate(t) if self._on_navigate else None)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)

        self._build_charts(scroll)

    def _load_kpis(self) -> dict:
        from app.core.database import db
        year = datetime.datetime.now().year
        result = {}
        with db() as conn:
            for table, _, _ in SACRAMENTOS:
                try:
                    total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    year_col = YEAR_ORDER_COL[table]
                    este_anio = conn.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE {year_col}=?", (year,)
                    ).fetchone()[0]
                    result[table] = (total, este_anio)
                except Exception:
                    result[table] = (0, 0)
        return result

    def _load_chart_data(self) -> dict:
        from app.core.database import db
        result = {}
        with db() as conn:
            for table, _, _ in SACRAMENTOS:
                try:
                    year_col = YEAR_ORDER_COL[table]
                    rows = conn.execute(
                        f"SELECT {year_col}, COUNT(*) FROM {table} "
                        f"WHERE {year_col} IS NOT NULL AND CAST({year_col} AS TEXT) != '' "
                        f"GROUP BY {year_col} ORDER BY {year_col}"
                    ).fetchall()
                    result[table] = ([str(r[0]) for r in rows], [r[1] for r in rows])
                except Exception:
                    result[table] = ([], [])
        return result

    def _build_charts(self, parent):
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            return

        chart_data = self._load_chart_data()

        ctk.CTkLabel(parent, text="Registros por año",
                     font=("Roboto", 16, "bold"), text_color=_TEXT).pack(pady=(4, 8))

        charts_row = ctk.CTkFrame(parent, fg_color="transparent")
        charts_row.pack(fill="x", padx=30, pady=(0, 28))

        for i, (table, label, color) in enumerate(SACRAMENTOS):
            years, counts = chart_data.get(table, ([], []))

            fig, ax = plt.subplots(figsize=(2.2, 1.9), dpi=90)
            fig.patch.set_facecolor("#16213e")
            ax.set_facecolor("#1a1f36")

            if years:
                ax.bar(range(len(years)), counts, color=color, alpha=0.88, width=0.65)
                step = max(1, len(years) // 5)
                ax.set_xticks(range(0, len(years), step))
                ax.set_xticklabels(
                    [years[j] for j in range(0, len(years), step)],
                    rotation=45, ha="right", fontsize=6, color="#a0aec0",
                )
            else:
                ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes,
                        ha="center", va="center", color="#a0aec0", fontsize=8)

            ax.set_title(label, color="#e2e8f0", fontsize=8, pad=3, fontweight="bold")
            ax.tick_params(axis="y", labelsize=6, colors="#a0aec0")
            ax.tick_params(axis="x", bottom=False)
            for spine in ax.spines.values():
                spine.set_color("#2d3748")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            fig.tight_layout(pad=0.5)

            canvas_w = FigureCanvasTkAgg(fig, master=charts_row)
            canvas_w.draw()
            widget = canvas_w.get_tk_widget()
            widget.configure(bg="#16213e", highlightthickness=0)
            widget.grid(row=0, column=i, padx=6, sticky="nsew")
            charts_row.grid_columnconfigure(i, weight=1)
            plt.close(fig)

    def refresh_iglesia(self):
        self._iglesia_panel.refresh()


class _IglesiaPanel(ctk.CTkFrame):
    """Franja de datos de la iglesia que aparece en el Dashboard."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._logo_img = None
        self._foto_img = None
        self._build()
        self.refresh()

    def _build(self):
        self._inner = ctk.CTkFrame(self, corner_radius=10, fg_color=_HEADER,
                                   border_width=1, border_color="#2d3748")
        self._inner.pack(fill="x")

    def refresh(self):
        from app.core.iglesia import load as iglesia_load
        from app.utils.config import ASSETS_DIR

        for w in self._inner.winfo_children():
            w.destroy()
        self._logo_img = None
        self._foto_img = None

        cfg = iglesia_load()

        # ── Columna de imágenes: logo arriba, foto abajo ──────────────
        img_col = ctk.CTkFrame(self._inner, fg_color="transparent")
        img_col.pack(side="left", padx=(10, 6), pady=8)

        logo_file = cfg.get("logo_file")
        if logo_file:
            logo_path = ASSETS_DIR / logo_file
            if logo_path.exists():
                try:
                    from PIL import Image
                    img = Image.open(logo_path).convert("RGBA")
                    img = img.resize((60, 60), Image.LANCZOS)
                    self._logo_img = ctk.CTkImage(light_image=img, dark_image=img,
                                                  size=(60, 60))
                    ctk.CTkLabel(img_col, image=self._logo_img, text="",
                                 fg_color="transparent",
                                 width=64, height=64).pack()
                except Exception:
                    pass

        foto_file = cfg.get("foto_file")
        if foto_file:
            foto_path = ASSETS_DIR / foto_file
            if foto_path.exists():
                try:
                    from PIL import Image
                    fimg = Image.open(foto_path).convert("RGB")
                    fimg = fimg.resize((90, 58), Image.LANCZOS)
                    self._foto_img = ctk.CTkImage(light_image=fimg, dark_image=fimg,
                                                  size=(90, 58))
                    ctk.CTkLabel(img_col, image=self._foto_img, text="",
                                 fg_color="transparent").pack(pady=(4, 0))
                except Exception:
                    pass

        # ── Datos ────────────────────────────────────────────────────
        data_col = ctk.CTkFrame(self._inner, fg_color="transparent")
        data_col.pack(side="left", fill="both", expand=True, pady=8, padx=(4, 12))

        # Nombre
        nombre = cfg.get("nombre") or "—"
        ctk.CTkLabel(data_col, text=nombre,
                     font=("Roboto", 13, "bold"), text_color=_RED,
                     anchor="w").pack(fill="x")

        # Dirección / ciudad / cp  (solo si hay algo)
        ciudad    = cfg.get("ciudad")    or ""
        direccion = cfg.get("direccion") or ""
        cp        = cfg.get("codigo_postal") or ""
        linea2_parts = [p for p in [direccion, ciudad, cp] if p]
        if linea2_parts:
            ctk.CTkLabel(data_col, text="  ·  ".join(linea2_parts),
                         font=("Roboto", 10), text_color=_MUTED,
                         anchor="w").pack(fill="x")

        # Filas de contacto: fila 1 (párroco · tel · horario · secretaria)
        _row1 = [
            ("Párroco",    cfg.get("parroco_actual") or ""),
            ("Tel.",       cfg.get("telefono")       or ""),
            ("Horario",    cfg.get("horario_oficina")or ""),
            ("Secretaria", cfg.get("secretaria")     or ""),
        ]
        _row1 = [(k, v) for k, v in _row1 if v]

        # Fila 2 (email · facebook · instagram)
        _row2 = [
            ("Email",     cfg.get("email")     or ""),
            ("Facebook",  cfg.get("facebook")  or ""),
            ("Instagram", cfg.get("instagram") or ""),
        ]
        _row2 = [(k, v) for k, v in _row2 if v]

        for items in (_row1, _row2):
            if not items:
                continue
            row_frame = ctk.CTkFrame(data_col, fg_color="transparent")
            row_frame.pack(fill="x")
            for i, (key, val) in enumerate(items):
                if i > 0:
                    ctk.CTkLabel(row_frame, text="│", font=("Roboto", 10),
                                 text_color="#4a5568").pack(side="left", padx=3)
                ctk.CTkLabel(row_frame, text=f"{key}: ", font=("Roboto", 10, "bold"),
                             text_color=_MUTED).pack(side="left")
                ctk.CTkLabel(row_frame, text=val, font=("Roboto", 10),
                             text_color=_TEXT).pack(side="left")


class _KpiCard(ctk.CTkFrame):
    def __init__(self, master, label: str, total: int, este_anio: int,
                 color: str, on_click=None, **kwargs):
        super().__init__(master, corner_radius=12, fg_color=_CARD_BG,
                         border_width=1, border_color=color, **kwargs)

        ctk.CTkFrame(self, height=5, fg_color=color, corner_radius=0).pack(fill="x")

        ctk.CTkLabel(self, text=label,
                     font=("Roboto", 13, "bold"), text_color=_MUTED).pack(pady=(14, 0), padx=16)

        ctk.CTkLabel(self, text=f"{total:,}",
                     font=("Roboto", 40, "bold"), text_color=color).pack(pady=(6, 0))

        ctk.CTkLabel(self, text="registros totales",
                     font=("Roboto", 10), text_color="gray").pack()

        ctk.CTkFrame(self, height=1, fg_color="gray25").pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(self, text=f"{este_anio:,} este año",
                     font=("Roboto", 12), text_color=_TEXT).pack(pady=(0, 10))

        ctk.CTkButton(
            self, text="Ver registros", height=30, corner_radius=8,
            fg_color=color, text_color="black" if color == "#f59e0b" else "white",
            hover_color=color,
            command=on_click,
        ).pack(pady=(0, 16), padx=20, fill="x")


# ── Popup de detalle ───────────────────────────────────────────────────────

def _show_detail_popup(parent, table: str, data: dict):
    popup = ctk.CTkToplevel(parent)
    popup.title("Detalle del registro")
    popup.geometry("480x520")
    popup.grab_set()

    ctk.CTkLabel(popup, text=table.replace("_", " ").title(),
                 font=("Roboto", 16, "bold")).pack(pady=(16, 8))

    frame = ctk.CTkScrollableFrame(popup)
    frame.pack(fill="both", expand=True, padx=16, pady=4)

    skip = {"id", "fuente_archivo"}
    for key, val in data.items():
        if key in skip or val is None:
            continue
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=key.replace("_", " ").capitalize() + ":",
                     font=("Roboto", 11, "bold"), width=160, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=str(val), anchor="w",
                     font=("Roboto", 11)).pack(side="left", fill="x", expand=True)

    ctk.CTkButton(popup, text="Cerrar", command=popup.destroy).pack(pady=12)
