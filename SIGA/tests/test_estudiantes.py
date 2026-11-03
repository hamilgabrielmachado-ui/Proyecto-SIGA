import pytest
from services import estudiante_service as es
from utils.excepciones import DuplicadoError, ValidacionError

BASE = {"codigo": "E-100", "nombres": "Juan Carlos", "apellidos": "Prueba López", "sexo": "M"}


def test_crear_y_buscar(admin):
    es.crear(admin, BASE)
    assert any(e["codigo"] == "E-100" for e in es.listar(admin, "Prueba"))


def test_codigo_y_cedula_duplicados(admin):
    es.crear(admin, {**BASE, "cedula": "001-010101-0001A"})
    with pytest.raises(DuplicadoError):
        es.crear(admin, BASE)
    with pytest.raises(DuplicadoError):
        es.crear(admin, {**BASE, "codigo": "E-101", "cedula": "001-010101-0001a"})


def test_validaciones(admin):
    with pytest.raises(ValidacionError):
        es.crear(admin, {**BASE, "correo": "no-es-correo"})
    with pytest.raises(ValidacionError):
        es.crear(admin, {**BASE, "nombres": "  "})
    with pytest.raises(ValidacionError):
        es.crear(admin, {**BASE, "sexo": ""})


def test_nombres_y_sexo(admin):
    for malo in ({"nombres": "Juan"}, {"nombres": "Juan Carlos Luis"}, {"apellidos": "López"},
                 {"nombres": "Juan 3"}, {"sexo": "F"}):
        with pytest.raises(ValidacionError):
            es.crear(admin, {**BASE, **malo})
    es.crear(admin, {**BASE, "codigo": "E-101", "nombres": "Juan Juan"})      # repetidos permitidos


def test_cedula_telefono_correo(admin):
    for malo in ({"cedula": "0010101010001A"}, {"cedula": "001-320101-0001A"}, {"cedula": "001-010101-0001"},
                 {"telefono": "1234567"}, {"telefono": "98887777"}, {"telefono": "8888-777"},
                 {"correo": "mario@gmail"}):
        with pytest.raises(ValidacionError):
            es.crear(admin, {**BASE, **malo})
    es.crear(admin, {**BASE, "cedula": "001-010101-0002B", "telefono": "88887777",
                     "correo": "Mario.Rodriguez@gmail.com"})
    with pytest.raises(DuplicadoError):
        es.crear(admin, {**BASE, "codigo": "E-102", "correo": "mario.rodriguez@gmail.com"})


def test_eliminar_con_dependencias_bloquea(admin):
    con_matricula = es.listar(admin, "Ana")[0]["id"]
    with pytest.raises(ValidacionError):
        es.eliminar(admin, con_matricula)
    nuevo = es.crear(admin, BASE)["id"]
    es.eliminar(admin, nuevo)
