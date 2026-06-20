"""Diálogo de configuración de la iglesia (nombre, contacto, logo, foto)."""
import shutil
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image

from app.core.iglesia import load as iglesia_load, save as iglesia_save
from app.utils.config import ASSETS_DIR

_FIELDS = [
    ("nombre",          "Nombre de la Iglesia"),
    ("ciudad",          "Ciudad"),
    ("direccion",       "Dirección"),
    ("codigo_postal",   "Código Postal"),
    ("parroco_actual",  "Párroco Actual"),
    ("telefono",        "Teléfono"),
    ("horario_oficina", "Horario de Oficina"),
    ("secretaria",      "Nombre de la Secretaria"),
]

_IMG_TYPES = [("Imagen", "*.png *.jpg *.jpeg *.bmp *.webp")]

_LOGO_FILE = "logo_parroquia.png"
_FOTO_FILE = "foto_parroquia.jpg"

_BG    = "#0f0f1a"
_HDR   = "#1a1a2e"
_MUTED = "#a0aec0"
_TEXT  = "#e2e8f0"
_RED   = "#e94560"


class IglesiaSettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_saved=None):
        super().__init__(parent)
        self.title("Configuración de la Iglesia")
        self.geometry("560x700")
        self.resizable(False, False)
        self.grab_set()

        self._on_saved = on_saved
        self._entries: dict[str, ctk.CTkEntry] = {}
        self._logo_src: str | None = None   # ruta original elegida
        self._foto_src: str | None = None
        self._logo_img: ctk.CTkImage | None = None
        self._foto_img: ctk.CTkImage | None = None

        self._build()
        self._load_data()

    # ── Construcción de la UI ─────────────────────────────────────────
    def _build(self):
        ctk.CTkLabel(self, text="Configuración de la Iglesia",
                     font=("Roboto", 15, "bold"), text_color=_RED).pack(pady=(16, 6))

        scroll = ctk.CTkScrollableFrame(self, fg_color=_BG)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        # ── Datos de la Iglesia ───────────────────────────────────────
        self._section_label(scroll, "Datos de la Iglesia")
        for col, label in _FIELDS:
            self._field_row(scroll, col, label)

        # ── Logotipo ──────────────────────────────────────────────────
        self._section_label(scroll, "Logotipo")
        logo_frame = ctk.CTkFrame(scroll, fg_color=_HDR, corner_radius=8)
        logo_frame.pack(fill="x", pady=(4, 8))

        self._logo_label = ctk.CTkLabel(
            logo_frame, text="Sin logo", width=120, height=120,
            fg_color="#16213e", corner_radius=6,
            text_color=_MUTED, font=("Roboto", 10),
        )
        self._logo_label.pack(side="left", padx=12, pady=12)

        logo_info = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_info.pack(side="left", fill="y", pady=12)
        ctk.CTkLabel(logo_info, text="Logo de la parroquia",
                     font=("Roboto", 11, "bold"), text_color=_TEXT,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(logo_info, text="Se usa en las constancias PDF.\nTamaño recomendado: 200×200 px.",
                     font=("Roboto", 10), text_color=_MUTED,
                     justify="left", anchor="w").pack(anchor="w", pady=(4, 8))
        ctk.CTkButton(logo_info, text="Seleccionar logo…", width=160,
                      fg_color="#1e40af", hover_color="#1e3a8a",
                      command=self._pick_logo).pack(anchor="w")

        # ── Foto de la parroquia ──────────────────────────────────────
        self._section_label(scroll, "Foto de la Parroquia")
        foto_frame = ctk.CTkFrame(scroll, fg_color=_HDR, corner_radius=8)
        foto_frame.pack(fill="x", pady=(4, 8))

        self._foto_label = ctk.CTkLabel(
            foto_frame, text="Sin foto", width=200, height=130,
            fg_color="#16213e", corner_radius=6,
            text_color=_MUTED, font=("Roboto", 10),
        )
        self._foto_label.pack(side="left", padx=12, pady=12)

        foto_info = ctk.CTkFrame(foto_frame, fg_color="transparent")
        foto_info.pack(side="left", fill="y", pady=12)
        ctk.CTkLabel(foto_info, text="Foto exterior / fachada",
                     font=("Roboto", 11, "bold"), text_color=_TEXT,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(foto_info, text="Imagen identificativa de la parroquia.",
                     font=("Roboto", 10), text_color=_MUTED,
                     anchor="w").pack(anchor="w", pady=(4, 8))
        ctk.CTkButton(foto_info, text="Seleccionar foto…", width=160,
                      fg_color="#1e40af", hover_color="#1e3a8a",
                      command=self._pick_foto).pack(anchor="w")

        # ── Botones ───────────────────────────────────────────────────
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkButton(btns, text="Guardar", fg_color="#4ade80", text_color="black",
                      command=self._save).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Cancelar",
                      command=self.destroy).pack(side="left")

    def _section_label(self, parent, text: str):
        ctk.CTkLabel(parent, text=text,
                     font=("Roboto", 12, "bold"), text_color="#93c5fd",
                     anchor="w").pack(fill="x", pady=(10, 2))
        ctk.CTkFrame(parent, height=1, fg_color="#2d3748").pack(fill="x", pady=(0, 6))

    def _field_row(self, parent, col: str, label: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=label + ":", width=170,
                     anchor="w", font=("Roboto", 11)).pack(side="left")
        entry = ctk.CTkEntry(row, font=("Roboto", 11))
        entry.pack(side="left", fill="x", expand=True)
        self._entries[col] = entry

    # ── Carga de datos guardados ──────────────────────────────────────
    def _load_data(self):
        cfg = iglesia_load()
        for col, entry in self._entries.items():
            val = cfg.get(col) or ""
            entry.delete(0, "end")
            entry.insert(0, str(val))

        logo_file = cfg.get("logo_file")
        if logo_file:
            logo_path = ASSETS_DIR / logo_file
            if logo_path.exists():
                self._show_logo_preview(str(logo_path))

        foto_file = cfg.get("foto_file")
        if foto_file:
            foto_path = ASSETS_DIR / foto_file
            if foto_path.exists():
                self._show_foto_preview(str(foto_path))

    # ── Selectores de imagen ──────────────────────────────────────────
    def _pick_logo(self):
        path = filedialog.askopenfilename(
            parent=self, title="Seleccionar logo",
            filetypes=_IMG_TYPES,
        )
        if path:
            self._logo_src = path
            self._show_logo_preview(path)

    def _pick_foto(self):
        path = filedialog.askopenfilename(
            parent=self, title="Seleccionar foto de la parroquia",
            filetypes=_IMG_TYPES,
        )
        if path:
            self._foto_src = path
            self._show_foto_preview(path)

    def _show_logo_preview(self, path: str):
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((120, 120), Image.LANCZOS)
            self._logo_img = ctk.CTkImage(light_image=img, dark_image=img,
                                          size=(img.width, img.height))
            self._logo_label.configure(image=self._logo_img, text="")
        except Exception:
            pass

    def _show_foto_preview(self, path: str):
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((200, 130), Image.LANCZOS)
            self._foto_img = ctk.CTkImage(light_image=img, dark_image=img,
                                          size=(img.width, img.height))
            self._foto_label.configure(image=self._foto_img, text="")
        except Exception:
            pass

    # ── Guardar ───────────────────────────────────────────────────────
    def _save(self):
        cfg = iglesia_load()

        for col, entry in self._entries.items():
            cfg[col] = entry.get().strip() or ""

        ASSETS_DIR.mkdir(exist_ok=True)

        if self._logo_src:
            dest = ASSETS_DIR / _LOGO_FILE
            shutil.copy2(self._logo_src, dest)
            cfg["logo_file"] = _LOGO_FILE

        if self._foto_src:
            dest = ASSETS_DIR / _FOTO_FILE
            shutil.copy2(self._foto_src, dest)
            cfg["foto_file"] = _FOTO_FILE

        iglesia_save(cfg)

        if self._on_saved:
            self._on_saved()
        self.destroy()
