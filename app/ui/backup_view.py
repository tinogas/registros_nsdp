"""Diálogo de respaldos, restauración y bitácora."""
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import customtkinter as ctk
from pathlib import Path

from app.core.backup import (
    create_backup, restore_backup, delete_backup,
    list_backups, get_log, clear_log,
)
from app.utils.config import BACKUPS_DIR
from app.ui.search_view import _style_treeview

_BG   = "#0f0f1a"
_HDR  = "#1a1a2e"
_MUTED = "#a0aec0"
_TEXT  = "#e2e8f0"
_RED   = "#e94560"


class BackupView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Respaldos y Restauración")
        self.geometry("920x520")
        self.resizable(True, True)
        self.minsize(700, 400)
        self.grab_set()
        self._odd_row, self._even_row = _style_treeview()
        self._build()
        self._refresh_backups()
        self._refresh_log()

    # ── UI ────────────────────────────────────────────────────────────────
    def _build(self):
        # Título
        ctk.CTkLabel(self, text="Respaldos y Restauración",
                     font=("Roboto", 15, "bold"), text_color=_RED).pack(pady=(14, 6))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # ── Panel izquierdo: lista de respaldos ───────────────────────
        left = ctk.CTkFrame(body, fg_color=_HDR, corner_radius=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(left, text="Respaldos disponibles",
                     font=("Roboto", 12, "bold"), text_color="#93c5fd",
                     anchor="w").pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkButton(left, text="+ Crear respaldo ahora",
                      fg_color="#4ade80", text_color="black", height=32,
                      command=self._do_create).pack(fill="x", padx=12, pady=(0, 6))

        tree_frame = tk.Frame(left, bg=_BG)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        self._backup_tree = ttk.Treeview(
            tree_frame,
            columns=("archivo", "fecha", "tamano"),
            show="headings",
            selectmode="browse",
            style="NsdpTree.Treeview",
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._backup_tree.yview,
                            style="NsdpTree.Vertical.TScrollbar")
        self._backup_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._backup_tree.pack(fill="both", expand=True)

        self._backup_tree.heading("archivo", text="Archivo")
        self._backup_tree.heading("fecha",   text="Fecha")
        self._backup_tree.heading("tamano",  text="Tamaño")
        self._backup_tree.column("archivo", width=170, anchor="w")
        self._backup_tree.column("fecha",   width=140, anchor="center")
        self._backup_tree.column("tamano",  width=72,  anchor="center")

        self._backup_tree.tag_configure("odd",  background=self._odd_row,
                                        foreground=_TEXT)
        self._backup_tree.tag_configure("even", background=self._even_row,
                                        foreground=_TEXT)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(2, 10))
        self._btn_restore = ctk.CTkButton(btn_row, text="Restaurar",
                                          fg_color="#1e40af", hover_color="#1e3a8a",
                                          state="disabled", width=100,
                                          command=self._do_restore)
        self._btn_restore.pack(side="left", padx=(0, 6))
        self._btn_delete = ctk.CTkButton(btn_row, text="Eliminar",
                                         fg_color="#f87171", text_color="black",
                                         state="disabled", width=80,
                                         command=self._do_delete)
        self._btn_delete.pack(side="left")

        self._backup_tree.bind("<<TreeviewSelect>>", self._on_backup_select)

        # ── Panel derecho: bitácora ───────────────────────────────────
        right = ctk.CTkFrame(body, fg_color=_HDR, corner_radius=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        log_header = ctk.CTkFrame(right, fg_color="transparent")
        log_header.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(log_header, text="Bitácora de operaciones",
                     font=("Roboto", 12, "bold"), text_color="#93c5fd",
                     anchor="w").pack(side="left")
        ctk.CTkButton(log_header, text="Limpiar", width=70, height=26,
                      fg_color="transparent", border_width=1,
                      border_color="gray40", text_color=_MUTED,
                      command=self._do_clear_log).pack(side="right")

        log_frame = tk.Frame(right, bg=_BG)
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        self._log_tree = ttk.Treeview(
            log_frame,
            columns=("fecha", "operacion", "archivo", "estado"),
            show="headings",
            selectmode="browse",
            style="NsdpTree.Treeview",
        )
        lvsb = ttk.Scrollbar(log_frame, orient="vertical",
                              command=self._log_tree.yview,
                              style="NsdpTree.Vertical.TScrollbar")
        self._log_tree.configure(yscrollcommand=lvsb.set)
        lvsb.pack(side="right", fill="y")
        self._log_tree.pack(fill="both", expand=True)

        self._log_tree.heading("fecha",     text="Fecha / Hora")
        self._log_tree.heading("operacion", text="Operación")
        self._log_tree.heading("archivo",   text="Archivo")
        self._log_tree.heading("estado",    text="Estado")
        self._log_tree.column("fecha",     width=140, anchor="center")
        self._log_tree.column("operacion", width=160, anchor="w")
        self._log_tree.column("archivo",   width=220, anchor="w")
        self._log_tree.column("estado",    width=60,  anchor="center")

        self._log_tree.tag_configure("odd",   background=self._odd_row,  foreground=_TEXT)
        self._log_tree.tag_configure("even",  background=self._even_row, foreground=_TEXT)
        self._log_tree.tag_configure("error", background="#3b0a0a",      foreground="#fca5a5")
        self._log_tree.tag_configure("ok",    background="#0a2e1a",      foreground="#86efac")

        # ── Status + cerrar ───────────────────────────────────────────
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.pack(fill="x", padx=14, pady=(0, 12))
        self._status = ctk.CTkLabel(foot, text="", text_color=_MUTED,
                                    font=("Roboto", 10))
        self._status.pack(side="left")
        ctk.CTkButton(foot, text="Cerrar", width=80,
                      command=self.destroy).pack(side="right")

    # ── Datos ─────────────────────────────────────────────────────────────
    def _refresh_backups(self):
        for item in self._backup_tree.get_children():
            self._backup_tree.delete(item)

        for i, path in enumerate(list_backups()):
            size_mb = path.stat().st_size / 1_048_576
            # Extraer fecha del nombre: registros_YYYYMMDD_HHMMSS.db
            try:
                stem = path.stem.replace("registros_", "")
                dt   = stem[:8] + "_" + stem[9:]
                fecha_str = f"{dt[:4]}-{dt[4:6]}-{dt[6:8]}  {dt[9:11]}:{dt[11:13]}"
            except Exception:
                fecha_str = path.stem
            tag = "odd" if i % 2 else "even"
            self._backup_tree.insert("", "end",
                                     values=(path.name, fecha_str, f"{size_mb:.2f} MB"),
                                     tags=(tag,))

        self._btn_restore.configure(state="disabled")
        self._btn_delete.configure(state="disabled")

    def _refresh_log(self):
        for item in self._log_tree.get_children():
            self._log_tree.delete(item)

        entries = get_log()
        # Mostrar más reciente primero
        for i, entry in enumerate(reversed(entries)):
            estado = entry.get("estado", "")
            base_tag = "odd" if i % 2 else "even"
            if estado == "ERROR":
                tag = "error"
            elif estado == "OK":
                tag = "ok"
            else:
                tag = base_tag
            self._log_tree.insert("", "end", values=(
                entry.get("fecha", ""),
                entry.get("operacion", ""),
                entry.get("archivo", ""),
                estado,
            ), tags=(tag,))

    def _on_backup_select(self, _=None):
        sel = self._backup_tree.selection()
        state = "normal" if sel else "disabled"
        self._btn_restore.configure(state=state)
        self._btn_delete.configure(state=state)

    def _selected_path(self) -> Path | None:
        sel = self._backup_tree.selection()
        if not sel:
            return None
        filename = self._backup_tree.item(sel[0], "values")[0]
        return BACKUPS_DIR / filename

    # ── Acciones ─────────────────────────────────────────────────────────
    def _do_create(self):
        self._status.configure(text="Creando respaldo…", text_color=_MUTED)
        def _run():
            ok, msg = create_backup()
            self.after(0, lambda: self._after_create(ok, msg))
        threading.Thread(target=_run, daemon=True).start()

    def _after_create(self, ok: bool, msg: str):
        if ok:
            self._status.configure(text=f"Respaldo creado: {msg}", text_color="#86efac")
        else:
            self._status.configure(text=f"Error: {msg}", text_color="#fca5a5")
        self._refresh_backups()
        self._refresh_log()

    def _do_restore(self):
        path = self._selected_path()
        if not path:
            return
        resp = messagebox.askyesno(
            "Confirmar restauración",
            f"¿Restaurar la base de datos desde\n«{path.name}»?\n\n"
            "La base de datos actual será reemplazada.\n"
            "Se recomienda reiniciar la aplicación después.",
            parent=self,
        )
        if not resp:
            return
        ok, msg = restore_backup(path)
        if ok:
            self._status.configure(
                text=f"Restauración OK — reinicia la app para aplicar los cambios.",
                text_color="#86efac")
        else:
            self._status.configure(text=f"Error: {msg}", text_color="#fca5a5")
        self._refresh_log()

    def _do_delete(self):
        path = self._selected_path()
        if not path:
            return
        resp = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el respaldo «{path.name}»?\nEsta acción no se puede deshacer.",
            parent=self,
        )
        if not resp:
            return
        ok, msg = delete_backup(path)
        if ok:
            self._status.configure(text=f"Respaldo eliminado: {msg}",
                                   text_color=_MUTED)
        else:
            self._status.configure(text=f"Error: {msg}", text_color="#fca5a5")
        self._refresh_backups()
        self._refresh_log()

    def _do_clear_log(self):
        resp = messagebox.askyesno("Limpiar bitácora",
                                   "¿Borrar todos los registros de la bitácora?",
                                   parent=self)
        if resp:
            clear_log()
            self._refresh_log()
            self._status.configure(text="Bitácora limpiada.", text_color=_MUTED)
