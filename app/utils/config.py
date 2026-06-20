from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "registros.db"
LAYOUTS_DIR = DATA_DIR / "layouts"
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
LAYOUTS_DIR.mkdir(exist_ok=True)
EXCEL_BACKUP_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)
