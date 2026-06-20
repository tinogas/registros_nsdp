import datetime
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
            header, text="Importar Excel", width=110,
            fg_color="transparent", border_width=1, border_color="gray40",
            hover_color="#1e1e3a", text_color=_MUTED,
            command=self._open_import,
        ).pack(side="right", padx=(0, 12), pady=10)

        ctk.CTkButton(
            header, text="Reportes", width=90,
            fg_color="transparent", border_width=1, border_color="gray40",
            hover_color="#1e1e3a", text_color=_MUTED,
            command=self._open_reports,
        ).pack(side="right", padx=(0, 6), pady=10)

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
        ctk.CTkLabel(self, text="Resumen general",
                     font=("Roboto", 20, "bold"), text_color=_TEXT).pack(pady=(28, 2))
        ctk.CTkLabel(self, text="Parroquia Nuestra Señora de la Paz — Hermosillo, Sonora",
                     font=("Roboto", 11), text_color="gray").pack(pady=(0, 20))

        kpis = self._load_kpis()

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=30, pady=(0, 20))

        for i, (table, label, color) in enumerate(SACRAMENTOS):
            total, este_anio = kpis.get(table, (0, 0))
            card = _KpiCard(cards, label=label, total=total, este_anio=este_anio,
                            color=color,
                            on_click=lambda t=table: self._on_navigate(t) if self._on_navigate else None)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)

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
