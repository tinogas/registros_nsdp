import customtkinter as ctk
from app.ui.search_view import SearchView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SACRAMENTOS = [
    ("matrimonios",      "Matrimonios"),
    ("primera_comunion", "1a Comunión"),
    ("confirmacion",     "Confirmación"),
    ("bautismos",        "Bautismos"),
    ("catecumenos",      "Catecúmenos"),
]


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NSDP — Registros Sacramentales")
        self.geometry("1100x680")
        self.minsize(900, 540)

        self._current_table = "bautismos"
        self._current_view = None
        self._build()
        self._show_table("bautismos")

    def _build(self):
        # Sidebar
        self._sidebar = ctk.CTkFrame(self, width=170, corner_radius=0)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        ctk.CTkLabel(self._sidebar, text="NSDP", font=("Roboto", 18, "bold"),
                     text_color="#e94560").pack(pady=(18, 4))
        ctk.CTkLabel(self._sidebar, text="Registros\nSacramentales",
                     font=("Roboto", 11), text_color="gray").pack(pady=(0, 20))

        self._sidebar_buttons = {}
        for table, label in SACRAMENTOS:
            btn = ctk.CTkButton(
                self._sidebar, text=label, anchor="w",
                fg_color="transparent", hover_color="#16213e",
                command=lambda t=table: self._show_table(t),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._sidebar_buttons[table] = btn

        ctk.CTkFrame(self._sidebar, height=1, fg_color="gray30").pack(fill="x", padx=12, pady=12)

        ctk.CTkButton(self._sidebar, text="Importar Excel", anchor="w",
                      fg_color="transparent", hover_color="#16213e",
                      command=self._open_import).pack(fill="x", padx=8, pady=2)

        # Área principal
        self._main = ctk.CTkFrame(self, corner_radius=0, fg_color="#0a0a1a")
        self._main.pack(side="left", fill="both", expand=True)

    def _show_table(self, table: str):
        self._current_table = table

        # Resaltar botón activo
        for t, btn in self._sidebar_buttons.items():
            btn.configure(fg_color="#1a1a2e" if t == table else "transparent")

        # Reemplazar vista
        if self._current_view:
            self._current_view.destroy()

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

    def _open_import(self):
        from app.ui.import_view import ImportDialog
        ImportDialog(self)


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

    ctk.CTkButton(popup, text="Cerrar",
                  command=popup.destroy).pack(pady=12)
