import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Ejecutable PyInstaller: datos junto al .exe, bundle en _MEIPASS
    BASE_DIR   = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS)
    # Layouts en AppData para que sobrevivan reinstalaciones del EXE
    _appdata = Path(os.environ.get("APPDATA", BASE_DIR)) / "NSDP"
    LAYOUTS_DIR = _appdata / "layouts"
else:
    BASE_DIR   = Path(__file__).resolve().parent.parent.parent
    BUNDLE_DIR = BASE_DIR
    LAYOUTS_DIR = BASE_DIR / "data" / "layouts"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "registros.db"
EXCEL_BACKUP_DIR = DATA_DIR / "excel_backup"
ASSETS_DIR = BASE_DIR / "assets"

EXCEL_FILES = [
    BASE_DIR / "SACRAMENTOS  2010 AL 2022 .xlsx",
    BASE_DIR / "SACRAMENTOS 2023.xlsx",
]

IGLESIA_JSON   = DATA_DIR / "iglesia.json"
BACKUPS_DIR    = DATA_DIR / "backups"
BITACORA_PATH  = BACKUPS_DIR / "bitacora.json"

DATA_DIR.mkdir(exist_ok=True)
LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)
EXCEL_BACKUP_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)
