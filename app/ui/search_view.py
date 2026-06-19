import customtkinter as ctk
from app.core.database import db

PAGE_SIZE = 25

# Columnas visibles y etiquetas por tabla
TABLE_COLS = {
    "matrimonios":     [("pareja", "Pareja"),    ("dia", "Día"), ("mes", "Mes"), ("anio", "Año"), ("parroco", "Párroco")],
    "primera_comunion":[("nombre", "Nombre"),    ("dia", "Día"), ("mes", "Mes"), ("anio", "Año"), ("mama", "Mamá"), ("papa", "Papá")],
    "confirmacion":    [("nombre", "Nombre"),    ("dia", "Día"), ("mes", "Mes"), ("anio", "Año"), ("parroco", "Párroco")],
    "bautismos":       [("nombre", "Nombre"),    ("dia_bautismo", "Día"), ("mes_bautismo", "Mes"), ("anio_bautismo", "Año"), ("parroco", "Párroco")],
    "catecumenos":     [("nombre", "Nombre"),    ("dia", "Día"), ("mes", "Mes"), ("anio", "Año")],
}

NAME_COL = {
    "matrimonios": "pareja",
    "primera_comunion": "nombre",
    "confirmacion": "nombre",
    "bautismos": "nombre",
    "catecumenos": "nombre",
}


class SearchView(ctk.CTkFrame):
    def __init__(self, master, table: str, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.table = table
        self.on_select = on_select
        self._page = 0
        self._rows = []
        self._selected_id: int | None = None
        self._build()
        self.load(page=0)

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 4))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.load(page=0))
        ctk.CTkEntry(top, textvariable=self._search_var,
                     placeholder_text="Buscar por nombre...",
                     width=300).pack(side="left")

        ctk.CTkLabel(top, text="Año:").pack(side="left", padx=(12, 4))
        self._year_var = ctk.StringVar(value="Todos")
        self._year_combo = ctk.CTkComboBox(top, variable=self._year_var,
                                           values=self._get_years(),
                                           command=lambda _: self.load(page=0),
                                           width=90)
        self._year_combo.pack(side="left")

        # tabla con scrollbar
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=4)

        cols = [c for c, _ in TABLE_COLS[self.table]]
        headers = [h for _, h in TABLE_COLS[self.table]]

        self._tree_frame = ctk.CTkScrollableFrame(frame)
        self._tree_frame.pack(fill="both", expand=True)

        self._header_row = ctk.CTkFrame(self._tree_frame, fg_color="#1a1a2e")
        self._header_row.pack(fill="x")
        for h in headers:
            ctk.CTkLabel(self._header_row, text=h, font=("Roboto", 12, "bold"),
                         anchor="w", width=180).pack(side="left", padx=4, pady=4)

        self._rows_frame = ctk.CTkFrame(self._tree_frame, fg_color="transparent")
        self._rows_frame.pack(fill="both", expand=True)

        # barra de acciones
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(4, 0))
        ctk.CTkButton(actions, text="+ Nuevo", width=90,
                      fg_color="#4ade80", text_color="black",
                      command=self._new_record).pack(side="left", padx=(0, 6))
        self._btn_edit = ctk.CTkButton(actions, text="Editar", width=80,
                                       state="disabled",
                                       command=self._edit_record)
        self._btn_edit.pack(side="left", padx=(0, 6))
        self._btn_print = ctk.CTkButton(actions, text="Imprimir constancia", width=150,
                                        state="disabled",
                                        command=self._print_record)
        self._btn_print.pack(side="left")

        # paginación
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=10, pady=(4, 8))
        ctk.CTkButton(nav, text="< Anterior", width=100,
                      command=self._prev_page).pack(side="left")
        self._page_label = ctk.CTkLabel(nav, text="Página 1")
        self._page_label.pack(side="left", padx=12)
        ctk.CTkButton(nav, text="Siguiente >", width=100,
                      command=self._next_page).pack(side="left")
        self._count_label = ctk.CTkLabel(nav, text="")
        self._count_label.pack(side="right")

    def _get_years(self):
        year_col = "anio_bautismo" if self.table == "bautismos" else "anio"
        try:
            with db() as conn:
                rows = conn.execute(
                    f"SELECT DISTINCT {year_col} FROM {self.table} WHERE {year_col} IS NOT NULL ORDER BY {year_col}"
                ).fetchall()
            return ["Todos"] + [str(r[0]) for r in rows]
        except Exception:
            return ["Todos"]

    def load(self, page: int = 0):
        self._page = page
        query_text = self._search_var.get().strip()
        year = self._year_var.get()
        name_col = NAME_COL[self.table]
        year_col = "anio_bautismo" if self.table == "bautismos" else "anio"
        cols = [c for c, _ in TABLE_COLS[self.table]]

        conditions = []
        params = []
        if query_text:
            conditions.append(f"{name_col} LIKE ?")
            params.append(f"%{query_text}%")
        if year and year != "Todos":
            conditions.append(f"{year_col} = ?")
            params.append(year)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        select_cols = ", ".join(["id"] + cols)
        with db() as conn:
            total = conn.execute(
                f"SELECT count(*) FROM {self.table} {where}", params
            ).fetchone()[0]
            rows = conn.execute(
                f"SELECT {select_cols} FROM {self.table} {where} "
                f"ORDER BY id LIMIT {PAGE_SIZE} OFFSET {page * PAGE_SIZE}",
                params,
            ).fetchall()

        self._total = total
        self._render_rows(rows, cols)
        self._page_label.configure(text=f"Página {page + 1} de {max(1, -(-total // PAGE_SIZE))}")
        self._count_label.configure(text=f"{total} registros")

    def _render_rows(self, rows, cols):
        for widget in self._rows_frame.winfo_children():
            widget.destroy()

        for i, row in enumerate(rows):
            bg = "#16213e" if i % 2 == 0 else "#0f3460"
            row_frame = ctk.CTkFrame(self._rows_frame, fg_color=bg, cursor="hand2")
            row_frame.pack(fill="x", pady=1)
            row_id = row[0]
            row_data = dict(zip(cols, row[1:]))
            for c in cols:
                val = str(row_data.get(c) or "")
                ctk.CTkLabel(row_frame, text=val, anchor="w",
                             width=180, font=("Roboto", 11)).pack(side="left", padx=4, pady=3)
            row_frame.bind("<Button-1>", lambda e, rid=row_id: self._select(rid))
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", lambda e, rid=row_id: self._select(rid))

    def _select(self, row_id: int):
        self._selected_id = row_id
        self._btn_edit.configure(state="normal")
        self._btn_print.configure(state="normal")
        if self.on_select:
            self.on_select(self.table, row_id)

    def _new_record(self):
        from app.ui.form_view import FormDialog
        FormDialog(self.winfo_toplevel(), self.table,
                   on_saved=lambda: self.load(self._page))

    def _edit_record(self):
        if self._selected_id is None:
            return
        from app.ui.form_view import FormDialog
        FormDialog(self.winfo_toplevel(), self.table,
                   row_id=self._selected_id,
                   on_saved=lambda: self.load(self._page))

    def _print_record(self):
        if self._selected_id is None:
            return
        from app.pdf.renderer import generate_constancia
        generate_constancia(self.table, self._selected_id)

    def _prev_page(self):
        if self._page > 0:
            self.load(self._page - 1)

    def _next_page(self):
        if (self._page + 1) * PAGE_SIZE < self._total:
            self.load(self._page + 1)
