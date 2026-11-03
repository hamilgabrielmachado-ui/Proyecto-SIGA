"""Motor y sesiones de SQLAlchemy."""
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config import settings

_url = make_url(settings.get_database_url())
_kwargs = {"pool_pre_ping": True}
_es_sqlite = _url.get_backend_name() == "sqlite"
if _es_sqlite:
    _kwargs = {"connect_args": {"check_same_thread": False}}
    if _url.database in (None, "", ":memory:"):
        _kwargs["poolclass"] = StaticPool

engine = create_engine(_url, **_kwargs)

if _es_sqlite:
    @event.listens_for(engine, "connect")
    def _activar_fk(dbapi_con, _):
        dbapi_con.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session():
    """Sesión con commit automático y rollback si ocurre un error."""
    sesion = SessionLocal()
    try:
        yield sesion
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()


def probar_conexion() -> None:
    """Lanza una excepción si no se puede conectar a la base de datos."""
    with engine.connect() as con:
        con.execute(text("SELECT 1"))
