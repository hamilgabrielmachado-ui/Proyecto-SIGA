"""Configuración central de SIGA. Lee las variables del archivo .env."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "siga_db")

# Solo para pruebas automáticas o desarrollo: permite usar otra base (p. ej. SQLite).
DATABASE_URL_OVERRIDE = os.getenv("DATABASE_URL")

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

MAX_INTENTOS_LOGIN = 5
MINUTOS_BLOQUEO = 5

REPORTS_DIR = BASE_DIR / "reports"
BACKUPS_DIR = BASE_DIR / "backups"
STYLES_DIR = BASE_DIR / "resources" / "styles"


def get_database_url():
    """Devuelve la URL de conexión (maneja caracteres especiales en la clave)."""
    if DATABASE_URL_OVERRIDE:
        return DATABASE_URL_OVERRIDE
    return URL.create(
        "mysql+pymysql", username=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, database=DB_NAME, query={"charset": "utf8mb4"},
    )
