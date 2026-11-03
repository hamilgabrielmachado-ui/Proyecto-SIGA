"""Base de los controladores: convierte excepciones de los servicios en mensajes para la vista."""
import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from utils.excepciones import SigaError

log = logging.getLogger("siga")


@dataclass
class Resultado:
    ok: bool
    datos: Any = None
    mensaje: str = ""


def ejecutar(funcion, *args, ok="", vacio=None, **kwargs) -> Resultado:
    try:
        return Resultado(True, funcion(*args, **kwargs), ok)
    except SigaError as e:
        return Resultado(False, vacio, str(e))
    except DBAPIError:
        log.exception("Error de conexión o consulta")
        return Resultado(False, vacio, "No se pudo comunicar con la base de datos. Verifique que MySQL "
                                       "esté activo e intente de nuevo.")
    except SQLAlchemyError:
        log.exception("Error de base de datos")
        return Resultado(False, vacio, "Ocurrió un problema al guardar o consultar los datos.")
    except Exception:
        log.exception("Error inesperado")
        return Resultado(False, vacio, "Ocurrió un error inesperado. Si continúa, contacte al administrador.")


class ControladorBase:
    def __init__(self, actor):
        self.actor = actor

    def _run(self, fn, *args, ok="", vacio=None, **kw):
        return ejecutar(fn, self.actor, *args, ok=ok, vacio=vacio, **kw)
