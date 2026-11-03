"""Respaldos de la base de datos (mysqldump para MySQL; copia de archivo para SQLite)."""
import os
import shutil
import subprocess
from datetime import datetime

from sqlalchemy.engine import make_url

from config import settings
from database.connection import get_session
from services import auditoria_service
from services.permisos_service import requerir
from utils.excepciones import ValidacionError


def crear_respaldo(actor):
    requerir(actor, "respaldos.gestionar")
    settings.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    url = make_url(settings.get_database_url())
    if url.get_backend_name() == "sqlite":
        if not url.database or url.database == ":memory:":
            raise ValidacionError("No se puede respaldar una base de datos en memoria.")
        destino = settings.BACKUPS_DIR / f"siga_{marca}.sqlite3"
        shutil.copyfile(url.database, destino)
    else:
        destino = settings.BACKUPS_DIR / f"siga_{marca}.sql"
        cmd = ["mysqldump", f"--host={url.host}", f"--port={url.port or 3306}", f"--user={url.username}",
               "--single-transaction", "--routines", f"--result-file={destino}", url.database]
        try:
            res = subprocess.run(cmd, env={**os.environ, "MYSQL_PWD": url.password or ""},
                                 capture_output=True, text=True, timeout=300)
        except FileNotFoundError:
            raise ValidacionError("No se encontró «mysqldump». Instale las herramientas de MySQL y "
                                  "agregue su carpeta «bin» al PATH del sistema.")
        except subprocess.TimeoutExpired:
            raise ValidacionError("El respaldo tardó demasiado y fue cancelado.")
        if res.returncode != 0:
            destino.unlink(missing_ok=True)
            raise ValidacionError("No se pudo crear el respaldo. Verifique la conexión y los permisos.")
    with get_session() as s:
        auditoria_service.registrar(s, actor, "RESPALDO_CREADO", "respaldo", None, destino.name)
    return destino
