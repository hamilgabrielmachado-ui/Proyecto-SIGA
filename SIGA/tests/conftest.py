import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.sqlite3"
os.environ["ADMIN_PASSWORD"] = "Admin1234"

import pytest  # noqa: E402

from database.base import Base  # noqa: E402
from database.connection import engine  # noqa: E402


@pytest.fixture()
def db():
    """Base limpia con datos base y datos de demostración en cada prueba."""
    Base.metadata.drop_all(engine)
    from database.seed_demo import sembrar
    sembrar()
    yield


@pytest.fixture()
def admin(db):
    from services import autenticacion_service as a
    return a.iniciar_sesion("admin", "Admin1234")


@pytest.fixture()
def docente(db):
    from services import autenticacion_service as a
    return a.iniciar_sesion("docente", "Demo1234")


@pytest.fixture()
def estudiante(db):
    from services import autenticacion_service as a
    return a.iniciar_sesion("estudiante", "Demo1234")
