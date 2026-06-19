import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import customtkinter as ctk
from app.core.database import db

PAGE_SIZE = 25

# Columnas visibles por tabla (folio siempre primero)
TABLE_COLS = {
    "matrimonios":     [("folio", "Folio"), ("pareja", "Pareja"),       ("dia", "Día"), ("mes", "Mes"),          ("anio", "Año"), ("parroco", "Párroco")],
    "primera_comunion":[("folio", "Folio"), ("nombre", "Nombre"),       ("dia", "Día"), ("mes", "Mes"),          ("anio", "Año"), ("mama", "Mamá"),      ("papa", "Papá")],
    "confirmacion":    [("folio", "Folio"), ("nombre", "Nombre"),       ("dia", "Día"), ("mes", "Mes"),          ("anio", "Año"), ("parroco", "Párroco")],
    "bautismos":       [("folio", "Folio"), ("nombre", "Nombre"),       ("dia_bautismo", "Día"), ("mes_bautismo", "Mes"), ("anio_bautismo", "Año"), ("parroco", "Párroco")],
    "catecumenos":     [("folio", "Folio"), ("nombre", "Nombre"),       ("dia", "Día"), ("mes", "Mes"),          ("anio", "Año")],
}

NAME_COL = {
    "matrimonios":      "pareja",
    "primera_comunion": "nombre",
    "confirmacion":     "nombre",
    "bautismos":        "nombre",
    "catecumenos":      "nombre",
}

YEAR_ORDER_COL = {
    "matrimonios":      "anio",
    "primera_comunion": "anio",
    "confirmacion":     "anio",
    "bautismos":        "anio_bautismo",
    "catecumenos":      "anio",
}

# Ancho en píxeles por columna
COL_WIDTHS = {
    "folio":          55,
    "nombre":        260,
    "pareja":        300,
    "dia":            45,
    "mes":           120,
    "anio":           55,
    "anio_bautismo":  55,
    "dia_bautismo":   45,
    "mes_bautismo":  120,
    "mama":          175,
    "papa":          175,
    "parroco":       165,
    "padre":         155,
    "madre":         155,
}
DEFAULT_COL_WIDTH = 130


def _style_treeview():
    """Aplica tema oscuro al ttk.Treeview."""
    style = ttk.Style()
    style.theme_use("clam")

    bg       = "#0f0f1a"
    fg       = "#e2e8f0"
    selected = "#1e40af"
    header   = "#1a1a2e"
    odd_row  = "#16213e"
    even_row = "#0f172a"
    border   = "#2d3748"

    style.configure("NsdpTree.Treeview",
                    background=even_row,
                    foreground=fg,
                    fieldbackground=even_row,
                    borderwidth=0,
                    rowheight=26,
                    font=("Segoe UI", 10))

    style.configure("NsdpTree.Treeview.Heading",
                    background=header,
                    foreground="#93c5fd",
                    relief="flat",
                    font=("Segoe UI", 10, "bold"))

    style.map("NsdpTree.Treeview",
              background=[("selected", selected)],
              foreground=[("selected", "#ffffff")])

    style.map("NsdpTree.Treeview.Heading",
              background=[("active", "#253360")])

    style.configure("NsdpTree.Vertical.TScrollbar",
                    background=border,
                    troughcolor=bg,
                    arrowcolor=fg,
                    borderwidth=0)

    return odd_row, even_row


class SearchView(ctk.CTkFrame):
    def __init__(self, master, table: str, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.table = table
        self.on_select = on_select
        self._page = 0
        self._total = 0
        self._selected_id: int | None = None
        self._row_ids: list[int] = []
        self._odd_row, self._even_row = _style_treeview()
        self._build()
        self.load(page=0)

    # ------------------------------------------------------------------
    def _build(self):
        # ── Barra de búsqueda ──────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 6))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.load(page=0))
        ctk.CTkEntry(top, textvariable=self._search_var,
                     placeholder_text="Buscar por nombre...",
                     width=300).pack(side="left")

        ctk.CTkLabel(top, text="Año:").pack(side="left", padx=(14, 4))
        self._year_var = ctk.StringVar(value="Todos")
        self._year_combo = ctk.CTkComboBox(top, variable=self._year_var,
                                           values=self._get_years(),
                                           command=lambda _: self.load(page=0),
                                           width=95)
        self._year_combo.pack(side="left")

        # ── Treeview ───────────────────────────────────────────────
        tree_frame = tk.Frame(self, bg="#0f0f1a")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        cols = [c for c, _ in TABLE_COLS[self.table]]
        headers = {c: h for c, h in TABLE_COLS[self.table]}

        self._tree = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            selectmode="browse",
            style="NsdpTree.Treeview",
        )

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._tree.yview,
                            style="NsdpTree.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(side="left", fill="both", expand=True)

        # Anclas por columna (sin ancho fijo aún — se calcula en _autosize_columns)
        for col in cols:
            anchor = "center" if col in ("folio", "dia", "dia_bautismo", "anio", "anio_bautismo") else "w"
            self._tree.heading(col, text=headers[col], anchor=anchor)
            self._tree.column(col, width=80, minwidth=40, anchor=anchor, stretch=False)

        # Tags para filas alternas
        self._tree.tag_configure("odd",  background=self._odd_row,  foreground="#e2e8f0")
        self._tree.tag_configure("even", background=self._even_row, foreground="#e2e8f0")
        self._tree.tag_configure("sel",  background="#1e40af",       foreground="#ffffff")

        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._tree.bind("<Double-1>",          self._on_double_click)

        # ── Acciones ───────────────────────────────────────────────
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(2, 0))

        ctk.CTkButton(actions, text="+ Nuevo", width=90,
                      fg_color="#4ade80", text_color="black",
                      command=self._new_record).pack(side="left", padx=(0, 6))
        self._btn_edit = ctk.CTkButton(actions, text="Editar", width=80,
                                       state="disabled",
                                       command=self._edit_record)
        self._btn_edit.pack(side="left", padx=(0, 6))
        self._btn_print = ctk.CTkButton(actions, text="Imprimir constancia", width=160,
                                        state="disabled",
                                        command=self._print_record)
        self._btn_print.pack(side="left")

        # ── Paginación ─────────────────────────────────────────────
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=10, pady=(4, 8))

        ctk.CTkButton(nav, text="< Anterior", width=100,
                      command=self._prev_page).pack(side="left")
        self._page_label = ctk.CTkLabel(nav, text="Página 1")
        self._page_label.pack(side="left", padx=12)
        ctk.CTkButton(nav, text="Siguiente >", width=100,
                      command=self._next_page).pack(side="left")
        self._count_label = ctk.CTkLabel(nav, text="", text_color="gray")
        self._count_label.pack(side="right")

    # ------------------------------------------------------------------
    def _get_years(self):
        year_col = YEAR_ORDER_COL[self.table]
        try:
            with db() as conn:
                rows = conn.execute(
                    f"SELECT DISTINCT {year_col} FROM {self.table} "
                    f"WHERE {year_col} IS NOT NULL ORDER BY {year_col}"
                ).fetchall()
            return ["Todos"] + [str(r[0]) for r in rows]
        except Exception:
            return ["Todos"]

    def load(self, page: int = 0):
        self._page = page
        query_text = self._search_var.get().strip()
        year       = self._year_var.get()
        name_col   = NAME_COL[self.table]
        year_col   = YEAR_ORDER_COL[self.table]
        cols       = [c for c, _ in TABLE_COLS[self.table]]

        conditions, params = [], []
        if query_text:
            conditions.append(f"{name_col} LIKE ?")
            params.append(f"%{query_text}%")
        if year and year != "Todos":
            conditions.append(f"{year_col} = ?")
            params.append(year)

        where      = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        select_cols = ", ".join(["id"] + cols)

        with db() as conn:
            self._total = conn.execute(
                f"SELECT count(*) FROM {self.table} {where}", params
            ).fetchone()[0]
            rows = conn.execute(
                f"SELECT {select_cols} FROM {self.table} {where} "
                f"ORDER BY {year_col} ASC, folio ASC "
                f"LIMIT {PAGE_SIZE} OFFSET {page * PAGE_SIZE}",
                params,
            ).fetchall()

        self._render_rows(rows, cols)
        total_pages = max(1, -(-self._total // PAGE_SIZE))
        self._page_label.configure(text=f"Página {page + 1} de {total_pages}")
        self._count_label.configure(text=f"{self._total} registros")

    def _render_rows(self, rows, cols):
        # Limpiar treeview
        for item in self._tree.get_children():
            self._tree.delete(item)

        self._row_ids = []
        for i, row in enumerate(rows):
            row_id   = row[0]
            values   = [str(row[j + 1]) if row[j + 1] is not None else "" for j in range(len(cols))]
            tag      = "odd" if i % 2 else "even"
            iid      = self._tree.insert("", "end", values=values, tags=(tag,))
            self._row_ids.append((iid, row_id))

        self._autosize_columns(cols, rows)

    def _autosize_columns(self, cols, rows):
        """Ajusta el ancho de cada columna al máximo entre encabezado y valores reales."""
        data_font = tkfont.Font(family="Segoe UI", size=10)
        head_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        PAD = 20   # padding interno por celda
        MIN = 40
        MAX = 420

        headers = {c: h for c, h in TABLE_COLS[self.table]}

        # Ancho inicial = ancho del encabezado
        col_widths = {c: head_font.measure(headers.get(c, c)) + PAD for c in cols}

        # Ampliar con el valor más largo de la página actual
        for row in rows:
            for j, col in enumerate(cols):
                val = str(row[j + 1]) if row[j + 1] is not None else ""
                w = data_font.measure(val) + PAD
                if w > col_widths[col]:
                    col_widths[col] = w

        # Consultar la BD por la longitud máxima de cada columna (todos los registros)
        year_col   = YEAR_ORDER_COL[self.table]
        name_col   = NAME_COL[self.table]
        query_text = self._search_var.get().strip()
        year       = self._year_var.get()

        conditions, params = [], []
        if query_text:
            conditions.append(f"{name_col} LIKE ?")
            params.append(f"%{query_text}%")
        if year and year != "Todos":
            conditions.append(f"{year_col} = ?")
            params.append(year)
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        length_exprs = ", ".join(
            f"MAX(LENGTH(CAST({c} AS TEXT)))" for c in cols
        )
        try:
            with db() as conn:
                maxlens = conn.execute(
                    f"SELECT {length_exprs} FROM {self.table} {where}", params
                ).fetchone()
            avg_char = data_font.measure("n")
            for i, col in enumerate(cols):
                max_len = maxlens[i] or 0
                estimated = avg_char * max_len + PAD
                if estimated > col_widths[col]:
                    col_widths[col] = estimated
        except Exception:
            pass

        for col in cols:
            w = max(MIN, min(MAX, col_widths[col]))
            self._tree.column(col, width=w, minwidth=MIN)

    # ------------------------------------------------------------------
    def _on_tree_select(self, _event=None):
        sel = self._tree.selection()
        if not sel:
            return
        iid = sel[0]
        row_id = next((rid for i, rid in self._row_ids if i == iid), None)
        if row_id is None:
            return
        self._selected_id = row_id
        self._btn_edit.configure(state="normal")
        self._btn_print.configure(state="normal")
        if self.on_select:
            self.on_select(self.table, row_id)

    def _on_double_click(self, _event=None):
        if self._selected_id is not None:
            self._edit_record()

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
        from app.ui.print_view import PrintView
        PrintView(self.winfo_toplevel(), self.table, self._selected_id)

    def _prev_page(self):
        if self._page > 0:
            self.load(self._page - 1)

    def _next_page(self):
        if (self._page + 1) * PAGE_SIZE < self._total:
            self.load(self._page + 1)
