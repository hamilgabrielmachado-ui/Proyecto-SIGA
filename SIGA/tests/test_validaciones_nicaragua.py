"""Validaciones pensadas para datos reales de Nicaragua (centros, profesores y utilidades)."""
import pytest

from services import catalogo_service as cat, profesor_service as ps
from utils import validaciones as v
from utils.excepciones import DuplicadoError, ValidacionError

PROF = {"nombres": "Mario José", "apellidos": "Rodríguez Pérez", "cedula": "001-150685-0003C",
        "codigo_mined": "LE-002-SEC-001", "telefono": "22661234", "especialidad": "Matemática 2",
        "nivel_academico": "Licenciatura", "anios_experiencia": 5}


def test_cedula_estructura_y_fecha():
    assert v.validar_cedula("001-150695-0001a") == "001-150695-0001A"
    for mala in ("001-150695-0001", "0011-50695-0001A", "001-310295-0001A", "001-150695-00011", "ABC-150695-0001A",
                 "001-150625-0001A", "000-150695-0001A", "001-150695-0000A"):
        with pytest.raises(ValidacionError):
            v.validar_cedula(mala)


def test_nombre_dos_palabras_y_solo_letras():
    assert v.validar_nombre_persona("juan  carlos", "Nombres") == "Juan Carlos"
    for malo in ("Juan", "Juan Carlos Luis", "Juan 2", "Juan-Carlos", ""):
        with pytest.raises(ValidacionError):
            v.validar_nombre_persona(malo, "Nombres")


def test_sexo_coherente_con_nombre():
    v.validar_sexo_con_nombre("M", "José María")
    v.validar_sexo_con_nombre("F", "María José")
    with pytest.raises(ValidacionError):
        v.validar_sexo_con_nombre("F", "Carlos Luis")
    with pytest.raises(ValidacionError):
        v.validar_sexo_con_nombre("M", "Sofía Isabel")


def test_telefono_y_correo():
    assert v.validar_telefono("88887777") == "88887777"
    for malo in ("1234567", "123456789", "98887777", "8888-7777", "8888777a", "88888888"):
        with pytest.raises(ValidacionError):
            v.validar_telefono(malo)
    assert v.validar_correo("MarioRodriguezProfe@gmail.com") == "mariorodriguezprofe@gmail.com"
    for malo in ("a@b", "a b@gmail.com", "a..b@gmail.com", "@gmail.com", "a@@gmail.com"):
        with pytest.raises(ValidacionError):
            v.validar_correo(malo)


def test_codigo_mined_y_especialidad():
    assert v.validar_codigo_mined("le-001-sec-001") == "LE-001-SEC-001"
    for malo in ("LE-1-SEC-001", "LE-001-SEC-0010", "LE001SEC001", "XX-001-SEC-001", "LE-000-SEC-001"):
        with pytest.raises(ValidacionError):
            v.validar_codigo_mined(malo)
    assert v.validar_especialidad("Informática 2") == "Informática 2"
    for malo in ("Mate 1 2", "Mat3", "123", "Ciencias #"):
        with pytest.raises(ValidacionError):
            v.validar_especialidad(malo)


def test_profesor_crear_y_duplicados(admin):
    ps.crear(admin, PROF)
    with pytest.raises(DuplicadoError):                                   # misma cédula
        ps.crear(admin, {**PROF, "codigo_mined": "LE-003-SEC-001"})
    with pytest.raises(DuplicadoError):                                   # mismo código MINED
        ps.crear(admin, {**PROF, "cedula": "001-150685-0004D"})
    for malo in ({"cedula": "DEMO-123"}, {"codigo_mined": "M-1001"}, {"nombres": "Mario"},
                 {"anios_experiencia": 30}, {"cedula": "001-150610-0005E"}):
        with pytest.raises(ValidacionError):
            ps.crear(admin, {**PROF, "cedula": "001-150685-0006F", "codigo_mined": "LE-004-SEC-001", **malo})


def test_centros_validaciones(admin):
    cat.crear(admin, "centros", {"nombre": "Colegio San José", "codigo": "CE-100",
                                 "direccion": "Del semáforo 2 cuadras al sur, Managua"})
    for malo in ({"nombre": "Colegio 123"}, {"nombre": "Co"}, {"codigo": "CE 100!"}, {"direccion": "@@@@"},
                 {"nombre": "Colegio Nuevo", "codigo": "ce-100"}):
        base = {"nombre": "Instituto Nuevo", "codigo": "CE-200", "direccion": "Barrio Monseñor Lezcano, Managua"}
        with pytest.raises((ValidacionError, DuplicadoError)):
            cat.crear(admin, "centros", {**base, **malo})
