import threading
import customtkinter as ctk
from app.core.importer import run_full_import
from app.utils.config import EXCEL_FILES


class ImportDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Importar datos desde Excel")
        self.geometry("520x420")
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Importación de Excel a base de datos",
                     font=("Roboto", 15, "bold")).pack(pady=(16, 4))

        ctk.CTkLabel(self, text="Archivos que se importarán:",
                     font=("Roboto", 11), text_color="gray").pack()
        for p in EXCEL_FILES:
            icon = "✓" if p.exists() else "✗"
            color = "#4ade80" if p.exists() else "#f87171"
            ctk.CTkLabel(self, text=f"  {icon}  {p.name}",
                         font=("Roboto", 11), text_color=color).pack(anchor="w", padx=24)

        self._log = ctk.CTkTextbox(self, height=220, font=("Courier", 11))
        self._log.pack(fill="both", expand=True, padx=16, pady=12)
        self._log.configure(state="disabled")

        self._btn = ctk.CTkButton(self, text="Iniciar importación",
                                  command=self._start)
        self._btn.pack(pady=(0, 16))

    def _log_line(self, msg: str):
        self._log.configure(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _start(self):
        self._btn.configure(state="disabled", text="Importando...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        def cb(msg):
            self.after(0, self._log_line, msg)

        try:
            result = run_full_import(cb)
            total = sum(n for tablas in result.values() for n in tablas.values())
            self.after(0, self._log_line, f"\nListo. Total importado: {total} registros.")
        except Exception as e:
            self.after(0, self._log_line, f"\nError: {e}")
        finally:
            self.after(0, lambda: self._btn.configure(state="normal", text="Importar de nuevo"))
