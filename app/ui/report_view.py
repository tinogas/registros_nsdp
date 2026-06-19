"""
Módulo de reportes: filtros por tipo, año y mes → tabla de resultados
→ exportar a PDF o Excel.
"""
import threading
import tempfile
from pathlib import Path
import customtkinter as ctk
from app.core.database import db

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

# Columnas del reporte por tabla
REPORT_COLS = {
    "matrimonios":     ["pareja",  "dia", "mes", "anio", "presbitero", "parroco"],
    "primera_comunion":["nombre",  "dia", "mes", "anio", "mama",       "papa", "parroco"],
    "confirmacion":    ["nombre",  "dia", "mes", "anio", "arzobispo",  "parroco"],
    "bautismos":       ["nombre",  "dia_bautismo", "mes_bautismo", "anio_bautismo", "padrino", "madrina", "parroco"],
    "catecumenos":     ["nombre",  "dia", "mes", "anio", "padre", "madre"],
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


class ReportView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reportes")
        self.geometry("900x620")
        self.grab_set()
        self._results = []
        self._table = "bautismos"
        self._build()

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

        # ── Tabla de resultados ───────────────────────────────────────
        tbl_frame = ctk.CTkFrame(self)
        tbl_frame.pack(fill="both", expand=True, padx=12, pady=4)

        self._scroll = ctk.CTkScrollableFrame(tbl_frame)
        self._scroll.pack(fill="both", expand=True)

        self._header_frame = ctk.CTkFrame(self._scroll, fg_color="#1a1a2e")
        self._header_frame.pack(fill="x")

        self._body_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._body_frame.pack(fill="both", expand=True)

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
        # Actualizar años disponibles
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
        for w in self._header_frame.winfo_children():
            w.destroy()
        for w in self._body_frame.winfo_children():
            w.destroy()

        col_width = max(100, min(160, 800 // len(cols)))

        # Encabezados
        for c in cols:
            ctk.CTkLabel(self._header_frame, text=c.replace("_", " ").title(),
                         width=col_width, font=("Roboto", 11, "bold"),
                         anchor="w").pack(side="left", padx=3, pady=4)

        # Filas (máx 500 en pantalla)
        for i, row in enumerate(self._results[:500]):
            bg = "#16213e" if i % 2 == 0 else "#0f3460"
            rf = ctk.CTkFrame(self._body_frame, fg_color=bg)
            rf.pack(fill="x", pady=1)
            for c in cols:
                val = str(row.get(c) or "")
                ctk.CTkLabel(rf, text=val, width=col_width,
                             font=("Roboto", 10), anchor="w").pack(side="left", padx=3, pady=2)

    # ------------------------------------------------------------------
    # Exportaciones
    # ------------------------------------------------------------------
    def _export_pdf(self):
        if not self._results:
            self._status.configure(text="Sin datos para exportar.")
            return
        threading.Thread(target=self._do_export_pdf, daemon=True).start()

    def _do_export_pdf(self):
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import LETTER, landscape
        from reportlab.lib import colors

        tabla_label = self._tabla_var.get()
        cols = REPORT_COLS[self._table]
        out = Path(tempfile.gettempdir()) / f"reporte_{self._table}.pdf"
        pw, ph = landscape(LETTER)

        c = rl_canvas.Canvas(str(out), pagesize=landscape(LETTER))
        col_w = (pw - 80) / len(cols)

        def draw_header(y):
            c.setFillColor(colors.HexColor("#1a1a2e"))
            c.rect(40, y - 4, pw - 80, 18, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 8)
            for i, col in enumerate(cols):
                c.drawString(42 + i * col_w, y + 2, col.replace("_", " ").upper()[:16])

        # Título
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        year = self._year_var.get()
        mes = self._mes_var.get()
        titulo = f"Reporte de {tabla_label}"
        if year != "Todos":
            titulo += f" — {year}"
        if mes != "Todos":
            titulo += f" / {mes}"
        c.drawString(40, ph - 40, titulo)
        c.setFont("Helvetica", 9)
        c.drawString(40, ph - 56, f"Total: {len(self._results)} registros")

        y = ph - 80
        draw_header(y)
        y -= 20

        c.setFont("Helvetica", 8)
        for i, row in enumerate(self._results):
            if y < 40:
                c.showPage()
                y = ph - 40
                draw_header(y)
                y -= 20
                c.setFont("Helvetica", 8)

            bg = colors.HexColor("#eef2ff") if i % 2 == 0 else colors.white
            c.setFillColor(bg)
            c.rect(40, y - 3, pw - 80, 14, fill=1, stroke=0)
            c.setFillColor(colors.black)
            for j, col in enumerate(cols):
                val = str(row.get(col) or "")[:24]
                c.drawString(42 + j * col_w, y + 1, val)
            y -= 14

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

        # Encabezados
        header_fill = PatternFill("solid", fgColor="1a1a2e")
        header_font = Font(bold=True, color="FFFFFF", size=10)
        for j, col in enumerate(cols, 1):
            cell = ws.cell(row=1, column=j, value=col.replace("_", " ").upper())
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions[cell.column_letter].width = 18

        # Datos
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
