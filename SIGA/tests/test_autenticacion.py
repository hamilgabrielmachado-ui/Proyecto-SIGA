import pytest
from services import autenticacion_service as auth
from utils.excepciones import AutenticacionError, ValidacionError


def test_login_correcto_y_roles(admin, docente, estudiante):
    assert admin.es_admin and docente.es_docente and estudiante.es_estudiante
    assert admin.debe_cambiar_password


def test_login_incorrecto_mensaje_generico(db):
    with pytest.raises(AutenticacionError) as e1:
        auth.iniciar_sesion("admin", "mala")
    with pytest.raises(AutenticacionError) as e2:
        auth.iniciar_sesion("noexiste", "mala")
    assert str(e1.value) == str(e2.value)


def test_bloqueo_por_intentos(db):
    for _ in range(5):
        with pytest.raises(AutenticacionError):
            auth.iniciar_sesion("docente", "x")
    with pytest.raises(AutenticacionError, match="bloqueada"):
        auth.iniciar_sesion("docente", "Demo1234")


def test_cambiar_password(admin):
    with pytest.raises(ValidacionError):
        auth.cambiar_password(admin, "Admin1234", "corta", "corta")
    auth.cambiar_password(admin, "Admin1234", "Nueva1234", "Nueva1234")
    assert auth.iniciar_sesion("admin", "Nueva1234").debe_cambiar_password is False


def test_password_nunca_en_texto_plano(db):
    from database.connection import get_session
    from models import Usuario
    with get_session() as s:
        for u in s.query(Usuario).all():
            assert u.password_hash.startswith("$2") and "Demo1234" not in u.password_hash
