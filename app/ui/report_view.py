"""
Módulo de reportes: filtros por tipo, año y mes → tabla de resultados
→ exportar a PDF o Excel.
"""
import threading
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import customtkinter as ctk
from app.core.database import db
from app.ui.search_view import _style_treeview

MESES = [
    "Todos", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
]

TABLAS = {
    "Matrimonios":    "matrimonios",
    "1a Comunión":    "primera_comunion",
    "Confirmación":   "confirmacion",
    "Bautismos":      "bautismos",
    "Catecúmenos":    "catecumenos",
}

REPORT_COLS = {
    "matrimonios":     ["pareja",  "dia", "mes", "anio", "presbitero", "parroco"],
    "primera_comunion":["nombre",  "dia", "mes", "anio", "mama",       "papa",    "parroco"],
    "confirmacion":    ["nombre",  "dia", "mes", "anio", "arzobispo",  "parroco"],
    "bautismos":       ["nombre",  "dia_bautismo", "mes_bautismo", "anio_bautismo", "padrino", "madrina", "parroco"],
    "catecumenos":     ["nombre",  "dia", "mes", "anio", "padre", "madre"],
}

REPORT_HEADERS = {
    "pareja":        "Pareja",
    "nombre":        "Nombre",
    "dia":           "Día",
    "mes":           "Mes",
    "anio":          "Año",
    "presbitero":    "Presbítero",
    "parroco":       "Párroco",
    "mama":          "Mamá",
    "papa":          "Papá",
    "arzobispo":     "Arzobispo",
    "dia_bautismo":  "Día",
    "mes_bautismo":  "Mes",
    "anio_bautismo": "Año",
    "padrino":       "Padrino",
    "madrina":       "Madrina",
    "padre":         "Padre",
    "madre":         "Madre",
}

YEAR_COL = {
    "matrimonios":     "anio",
    "primera_comunion":"anio",
    "confirmacion":    "anio",
    "bautismos":       "anio_bautismo",
    "catecumenos":     "anio",
}

MES_COL = {
    "matrimonios":     "mes",
    "primera_comunion":"mes",
    "confirmacion":    "mes",
    "bautismos":       "mes_bautismo",
    "catecumenos":     "mes",
}

# Columnas numéricas / cortas (ancla centrada en treeview y mínimo estrecho en PDF)
_CENTER_COLS = {"dia", "dia_bautismo", "anio", "anio_bautismo"}


class ReportView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reportes")
        self.geometry("960x640")
        self.grab_set()
        self._results: list[dict] = []
        self._table = "bautismos"
        self._odd_row, self._even_row = _style_treeview()
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        # ── Filtros ──────────────────────────────────────────────────
        filters = ctk.CTkFrame(self, fg_color="#1a1a2e")
        filters.pack(fill="x", padx=12, pady=(12, 4))

        ctk.CTkLabel(filters, text="Sacramento:").pack(side="left", padx=(8, 4))
        self._tabla_var = ctk.StringVar(value="Bautismos")
        ctk.CTkComboBox(filters, variable=self._tabla_var,
                        values=list(TABLAS.keys()), width=140,
                        command=self._on_table_change).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filters, text="Año:").pack(side="left", padx=(0, 4))
        self._year_var = ctk.StringVar(value="Todos")
        self._year_combo = ctk.CTkComboBox(filters, variable=self._year_var,
                                           values=["Todos"], width=90)
        self._year_combo.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filters, text="Mes:").pack(side="left", padx=(0, 4))
        self._mes_var = ctk.StringVar(value="Todos")
        ctk.CTkComboBox(filters, variable=self._mes_var,
                        values=MESES, width=130).pack(side="left", padx=(0, 12))

        ctk.CTkButton(filters, text="Buscar", width=80,
                      command=self._run_query).pack(side="left", padx=(0, 8))

        self._count_lbl = ctk.CTkLabel(filters, text="")
        self._count_lbl.pack(side="left")

        # ── Treeview ─────────────────────────────────────────────────
        tree_frame = tk.Frame(self, bg="#0f0f1a")
        tree_frame.pack(fill="both", expand=True, padx=12, pady=4)

        self._tree = ttk.Treeview(
            tree_frame,
            columns=[],
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

        # ── Exportar ─────────────────────────────────────────────────
        export = ctk.CTkFrame(self, fg_color="transparent")
        export.pack(fill="x", padx=12, pady=(4, 12))

        ctk.CTkButton(export, text="Exportar a PDF",
                      fg_color="#f97316", text_color="black",
                      command=self._export_pdf).pack(side="left", padx=(0, 8))
        ctk.CTkButton(export, text="Exportar a Excel",
                      fg_color="#4ade80", text_color="black",
                      command=self._export_excel).pack(side="left")

        self._status = ctk.CTkLabel(export, text="")
        self._status.pack(side="left", padx=12)

        # Carga inicial
        self._on_table_change("Bautismos")
        self._run_query()

    # ------------------------------------------------------------------
    def _on_table_change(self, label: str):
        self._table = TABLAS.get(label, "bautismos")
        year_col = YEAR_COL[self._table]
        try:
            with db() as conn:
                rows = conn.execute(
                    f"SELECT DISTINCT {year_col} FROM {self._table} "
                    f"WHERE {year_col} IS NOT NULL ORDER BY {year_col}"
                ).fetchall()
            years = ["Todos"] + [str(r[0]) for r in rows]
        except Exception:
            years = ["Todos"]
        self._year_combo.configure(values=years)
        self._year_var.set("Todos")

    def _run_query(self):
        table = self._table
        year = self._year_var.get()
        mes = self._mes_var.get()
        year_col = YEAR_COL[table]
        mes_col = MES_COL[table]
        cols = REPORT_COLS[table]

        conditions, params = [], []
        if year and year != "Todos":
            conditions.append(f"{year_col} = ?")
            params.append(year)
        if mes and mes != "Todos":
            conditions.append(f"UPPER({mes_col}) = ?")
            params.append(mes.upper())

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        select = ", ".join(cols)
        with db() as conn:
            rows = conn.execute(
                f"SELECT {select} FROM {table} {where} ORDER BY {year_col}, {mes_col}",
                params,
            ).fetchall()

        self._results = [dict(zip(cols, r)) for r in rows]
        self._count_lbl.configure(text=f"{len(self._results)} registros")
        self._render_table(cols)

    def _render_table(self, cols: list):
        # Reconfigurar columnas del treeview
        self._tree.configure(columns=cols)
        for col in cols:
            header = REPORT_HEADERS.get(col, col.replace("_", " ").title())
            anchor = "center" if col in _CENTER_COLS else "w"
            self._tree.heading(col, text=header, anchor=anchor)
            self._tree.column(col, width=80, minwidth=40, anchor=anchor, stretch=False)

        # Limpiar y poblar
        for item in self._tree.get_children():
            self._tree.delete(item)

        self._tree.tag_configure("odd",  background=self._odd_row,  foreground="#e2e8f0")
        self._tree.tag_configure("even", background=self._even_row, foreground="#e2e8f0")

        for i, row in enumerate(self._results[:2000]):
            values = [str(row.get(col) or "") for col in cols]
            tag = "odd" if i % 2 else "even"
            self._tree.insert("", "end", values=values, tags=(tag,))

        self._autosize_columns(cols)

    def _autosize_columns(self, cols: list):
        data_font = tkfont.Font(family="Segoe UI", size=10)
        head_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        PAD = 20
        MIN = 40
        MAX = 420

        col_widths = {}
        for col in cols:
            header = REPORT_HEADERS.get(col, col.replace("_", " ").title())
            col_widths[col] = head_font.measure(header) + PAD

        for row in self._results:
            for col in cols:
                val = str(row.get(col) or "")
                w = data_font.measure(val) + PAD
                if w > col_widths[col]:
                    col_widths[col] = w

        # Longitud máxima en todos los registros de la BD (filtro actual)
        year_col = YEAR_COL[self._table]
        mes_col = MES_COL[self._table]
        year = self._year_var.get()
        mes = self._mes_var.get()
        conditions, params = [], []
        if year and year != "Todos":
            conditions.append(f"{year_col} = ?")
            params.append(year)
        if mes and mes != "Todos":
            conditions.append(f"UPPER({mes_col}) = ?")
            params.append(mes.upper())
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        length_exprs = ", ".join(f"MAX(LENGTH(CAST({c} AS TEXT)))" for c in cols)
        try:
            with db() as conn:
                maxlens = conn.execute(
                    f"SELECT {length_exprs} FROM {self._table} {where}", params
                ).fetchone()
            avg_char = data_font.measure("n")
            for i, col in enumerate(cols):
                estimated = avg_char * (maxlens[i] or 0) + PAD
                if estimated > col_widths[col]:
                    col_widths[col] = estimated
        except Exception:
            pass

        for col in cols:
            w = max(MIN, min(MAX, col_widths[col]))
            self._tree.column(col, width=w, minwidth=MIN)

    # ------------------------------------------------------------------
    # Exportaciones
    # ------------------------------------------------------------------
    def _export_pdf(self):
        if not self._results:
            self._status.configure(text="Sin datos para exportar.")
            return
        threading.Thread(target=self._do_export_pdf, daemon=True).start()

    def _do_export_pdf(self):
        import io
        from itertools import groupby
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import LETTER, landscape
        from reportlab.lib import colors

        tabla_label = self._tabla_var.get()
        all_cols   = REPORT_COLS[self._table]
        has_parroco = "parroco" in all_cols

        # En tablas con párroco, el agrupador se muestra como encabezado de sección
        # y se omite de las columnas de cada fila → más espacio horizontal.
        cols = [c for c in all_cols if c != "parroco"] if has_parroco else all_cols

        out = Path(tempfile.gettempdir()) / f"reporte_{self._table}.pdf"
        pw, ph = landscape(LETTER)
        MARGIN  = 40
        USABLE  = pw - 2 * MARGIN
        ROW_H   = 14
        HDR_H   = 18
        GRP_H   = 16   # altura de la franja de grupo por párroco

        # ── Medir anchos de columna ────────────────────────────────────
        _buf = io.BytesIO()
        _mc  = rl_canvas.Canvas(_buf, pagesize=landscape(LETTER))

        desired: dict[str, float] = {}
        for col in cols:
            header = REPORT_HEADERS.get(col, col.replace("_", " ").title()).upper()
            w = _mc.stringWidth(header, "Helvetica-Bold", 8) + 14
            for row in self._results:
                val = str(row.get(col) or "")
                w_val = _mc.stringWidth(val, "Helvetica", 8) + 10
                if w_val > w:
                    w = w_val
            desired[col] = w

        total_desired = sum(desired.values()) or 1.0
        scale     = min(1.0, USABLE / total_desired)
        col_widths: dict[str, float] = {col: desired[col] * scale for col in cols}

        col_x: dict[str, float] = {}
        x = MARGIN + 2
        for col in cols:
            col_x[col] = x
            x += col_widths[col]

        # ── Funciones auxiliares de dibujo ─────────────────────────────
        def draw_col_header(y: float):
            c.setFillColor(colors.HexColor("#1a1a2e"))
            c.rect(MARGIN, y - 4, USABLE, HDR_H, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 8)
            for col in cols:
                label = REPORT_HEADERS.get(col, col.replace("_", " ").title()).upper()
                c.drawString(col_x[col], y + 2, label)

        def draw_group_header(y: float, nombre: str, n: int):
            c.setFillColor(colors.HexColor("#2d3a6e"))
            c.rect(MARGIN, y - 3, USABLE, GRP_H, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#93c5fd"))
            c.setFont("Helvetica-Bold", 9)
            c.drawString(MARGIN + 6, y + 2, f"Párroco: {nombre}  ({n} registros)")

        # ── Canvas y título ────────────────────────────────────────────
        c = rl_canvas.Canvas(str(out), pagesize=landscape(LETTER))

        year  = self._year_var.get()
        mes   = self._mes_var.get()
        titulo = f"Reporte de {tabla_label}"
        if year != "Todos":
            titulo += f" — {year}"
        if mes != "Todos":
            titulo += f" / {mes}"

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawString(MARGIN, ph - 40, titulo)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN, ph - 56, f"Total: {len(self._results)} registros")

        y = ph - 80
        draw_col_header(y)
        y -= HDR_H + 4

        # ── Datos ──────────────────────────────────────────────────────
        c.setFont("Helvetica", 8)

        if has_parroco:
            # Ordenar por párroco (sort estable: preserva orden año/mes dentro del grupo)
            sorted_rows = sorted(
                self._results,
                key=lambda r: (r.get("parroco") or "").upper(),
            )
            groups = groupby(sorted_rows, key=lambda r: r.get("parroco") or "Sin párroco")

            for parroco_nombre, grupo_iter in groups:
                grupo = list(grupo_iter)

                # Si no cabe el encabezado + al menos una fila → nueva página
                if y < GRP_H + ROW_H + 44:
                    c.showPage()
                    y = ph - 40
                    draw_col_header(y)
                    y -= HDR_H + 4
                    c.setFont("Helvetica", 8)

                draw_group_header(y, parroco_nombre, len(grupo))
                y -= GRP_H + 2

                for i, row in enumerate(grupo):
                    if y < 44:
                        c.showPage()
                        y = ph - 40
                        draw_col_header(y)
                        y -= HDR_H + 4
                        c.setFont("Helvetica", 8)

                    bg = colors.HexColor("#eef2ff") if i % 2 == 0 else colors.white
                    c.setFillColor(bg)
                    c.rect(MARGIN, y - 3, USABLE, ROW_H, fill=1, stroke=0)
                    c.setFillColor(colors.black)
                    for col in cols:
                        c.drawString(col_x[col], y + 1, str(row.get(col) or ""))
                    y -= ROW_H

                y -= 4   # separación visual entre grupos
        else:
            for i, row in enumerate(self._results):
                if y < 44:
                    c.showPage()
                    y = ph - 40
                    draw_col_header(y)
                    y -= HDR_H + 4
                    c.setFont("Helvetica", 8)

                bg = colors.HexColor("#eef2ff") if i % 2 == 0 else colors.white
                c.setFillColor(bg)
                c.rect(MARGIN, y - 3, USABLE, ROW_H, fill=1, stroke=0)
                c.setFillColor(colors.black)
                for col in cols:
                    c.drawString(col_x[col], y + 1, str(row.get(col) or ""))
                y -= ROW_H

        c.save()
        self.after(0, self._open_and_notify, out, "PDF")

    def _export_excel(self):
        if not self._results:
            self._status.configure(text="Sin datos para exportar.")
            return
        threading.Thread(target=self._do_export_excel, daemon=True).start()

    def _do_export_excel(self):
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment

        cols = REPORT_COLS[self._table]
        out = Path(tempfile.gettempdir()) / f"reporte_{self._table}.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self._tabla_var.get()[:31]

        header_fill = PatternFill("solid", fgColor="1a1a2e")
        header_font = Font(bold=True, color="FFFFFF", size=10)
        for j, col in enumerate(cols, 1):
            header = REPORT_HEADERS.get(col, col.replace("_", " ").title())
            cell = ws.cell(row=1, column=j, value=header.upper())
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions[cell.column_letter].width = 18

        alt_fill = PatternFill("solid", fgColor="EEF2FF")
        for i, row in enumerate(self._results, 2):
            fill = alt_fill if i % 2 == 0 else PatternFill()
            for j, col in enumerate(cols, 1):
                cell = ws.cell(row=i, column=j, value=row.get(col))
                cell.fill = fill

        wb.save(out)
        self.after(0, self._open_and_notify, out, "Excel")

    def _open_and_notify(self, path: Path, fmt: str):
        import os
        try:
            import win32api
            win32api.ShellExecute(0, "open", str(path), None, ".", 1)
        except Exception:
            os.startfile(str(path))
        self._status.configure(text=f"{fmt} generado: {path.name}")
