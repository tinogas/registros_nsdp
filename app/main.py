import sys
from pathlib import Path

# Asegurar que el directorio raíz está en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import init_db
from app.ui.app_window import AppWindow


def main():
    init_db()
    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
