import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Ejecutable PyInstaller instalado en Program Files (directorio de solo lectura).
    # Todos los archivos que la app escribe van a %APPDATA%\NSDP\ (siempre escribible).
    BASE_DIR   = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS)
    _user_dir  = Path(os.environ.get("APPDATA", BASE_DIR)) / "NSDP"
else:
    BASE_DIR   = Path(__file__).resolve().parent.parent.parent
    BUNDLE_DIR = BASE_DIR
    _user_dir  = BASE_DIR

DATA_DIR         = _user_dir / "data"
ASSETS_DIR       = _user_dir / "assets"
LAYOUTS_DIR      = DATA_DIR / "layouts"
EXCEL_BACKUP_DIR = DATA_DIR / "excel_backup"

DB_PATH       = DATA_DIR / "registros.db"
IGLESIA_JSON  = DATA_DIR / "iglesia.json"
BACKUPS_DIR   = DATA_DIR / "backups"
BITACORA_PATH = BACKUPS_DIR / "bitacora.json"

EXCEL_FILES = [
    BASE_DIR / "SACRAMENTOS  2010 AL 2022 .xlsx",
    BASE_DIR / "SACRAMENTOS 2023.xlsx",
]

DATA_DIR.mkdir(exist_ok=True)
LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)
EXCEL_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
