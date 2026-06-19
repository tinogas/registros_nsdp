import customtkinter as ctk
from app.core.database import db

# Campos editables por tabla (orden de presentación)
FIELDS = {
    "matrimonios": [
        ("numero",     "Número"),
        ("pareja",     "Pareja"),
        ("dia",        "Día"),
        ("mes",        "Mes"),
        ("anio",       "Año"),
        ("presbitero", "Presbítero"),
        ("testigo1",   "Testigo 1"),
        ("testigo2",   "Testigo 2"),
        ("testigo3",   "Testigo 3"),
        ("testigo4",   "Testigo 4"),
        ("parroco",    "Párroco"),
        ("libro",      "Libro"),
        ("pagina",     "Página"),
        ("partida",    "Partida"),
    ],
    "primera_comunion": [
        ("nombre",   "Nombre"),
        ("dia",      "Día"),
        ("mes",      "Mes"),
        ("anio",     "Año"),
        ("mama",     "Mamá"),
        ("papa",     "Papá"),
        ("padrinos", "Padrinos"),
        ("parroco",  "Párroco"),
    ],
    "confirmacion": [
        ("numero",    "Número"),
        ("nombre",    "Nombre"),
        ("dia",       "Día"),
        ("mes",       "Mes"),
        ("anio",      "Año"),
        ("papa",      "Papá"),
        ("mama",      "Mamá"),
        ("padrinos",  "Padrinos"),
        ("arzobispo", "Arzobispo"),
        ("parroco",   "Párroco"),
        ("libro",     "Libro"),
        ("pagina",    "Página"),
        ("partida",   "Partida"),
    ],
    "bautismos": [
        ("nombre",           "Nombre"),
        ("dia_nacimiento",   "Día nacimiento"),
        ("mes_nacimiento",   "Mes nacimiento"),
        ("anio_nacimiento",  "Año nacimiento"),
        ("lugar_nacimiento", "Lugar nacimiento"),
        ("papa",             "Papá"),
        ("mama",             "Mamá"),
        ("dia_bautismo",     "Día bautismo"),
        ("mes_bautismo",     "Mes bautismo"),
        ("anio_bautismo",    "Año bautismo"),
        ("ministro",         "Ministro"),
        ("padrino",          "Padrino"),
        ("madrina",          "Madrina"),
        ("parroco",          "Párroco"),
        ("registro_no",      "Registro No."),
        ("libro",            "Libro"),
        ("pagina",           "Página"),
        ("acta",             "Acta"),
    ],
    "catecumenos": [
        ("nombre",   "Nombre"),
        ("dia",      "Día"),
        ("mes",      "Mes"),
        ("anio",     "Año"),
        ("padre",    "Padre"),
        ("madre",    "Madre"),
        ("padrinos", "Padrinos"),
    ],
}


class FormDialog(ctk.CTkToplevel):
    """Diálogo para crear o editar un registro sacramental."""

    def __init__(self, parent, table: str, row_id: int = None, on_saved=None):
        super().__init__(parent)
        self.table = table
        self.row_id = row_id
        self.on_saved = on_saved
        self._entries: dict[str, ctk.CTkEntry] = {}

        title = "Nuevo registro" if row_id is None else "Editar registro"
        self.title(f"{title} — {table.replace('_', ' ').title()}")
        self.geometry("500x600")
        self.grab_set()

        self._build()
        if row_id is not None:
            self._load_data()

    def _build(self):
        ctk.CTkLabel(self, text=self.table.replace("_", " ").title(),
                     font=("Roboto", 15, "bold")).pack(pady=(14, 4))

        form = ctk.CTkScrollableFrame(self)
        form.pack(fill="both", expand=True, padx=16, pady=4)

        for col, label in FIELDS.get(self.table, []):
            row = ctk.CTkFrame(form, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label + ":", width=160,
                         anchor="w", font=("Roboto", 11)).pack(side="left")
            entry = ctk.CTkEntry(row, font=("Roboto", 11))
            entry.pack(side="left", fill="x", expand=True)
            self._entries[col] = entry

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=12)
        ctk.CTkButton(btns, text="Guardar", command=self._save,
                      fg_color="#4ade80", text_color="black").pack(side="left", padx=(0, 8))
        if self.row_id is not None:
            ctk.CTkButton(btns, text="Eliminar", command=self._delete,
                          fg_color="#f87171", text_color="black").pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Cancelar",
                      command=self.destroy).pack(side="left")

    def _load_data(self):
        with db() as conn:
            row = conn.execute(
                f"SELECT * FROM {self.table} WHERE id=?", (self.row_id,)
            ).fetchone()
        if not row:
            return
        data = dict(row)
        for col, entry in self._entries.items():
            val = data.get(col)
            entry.delete(0, "end")
            if val is not None:
                entry.insert(0, str(val))

    def _save(self):
        values = {col: entry.get().strip() or None
                  for col, entry in self._entries.items()}

        if self.row_id is None:
            cols = ", ".join(values.keys())
            placeholders = ", ".join("?" * len(values))
            with db() as conn:
                conn.execute(
                    f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})",
                    list(values.values()),
                )
        else:
            set_clause = ", ".join(f"{c}=?" for c in values)
            with db() as conn:
                conn.execute(
                    f"UPDATE {self.table} SET {set_clause} WHERE id=?",
                    list(values.values()) + [self.row_id],
                )

        if self.on_saved:
            self.on_saved()
        self.destroy()

    def _delete(self):
        dialog = ctk.CTkInputDialog(
            text=f"Escribe ELIMINAR para confirmar el borrado del registro #{self.row_id}:",
            title="Confirmar eliminación",
        )
        resp = dialog.get_input()
        if resp and resp.strip().upper() == "ELIMINAR":
            with db() as conn:
                conn.execute(f"DELETE FROM {self.table} WHERE id=?", (self.row_id,))
            if self.on_saved:
                self.on_saved()
            self.destroy()
