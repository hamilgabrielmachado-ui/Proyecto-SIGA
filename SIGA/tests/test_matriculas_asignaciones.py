import pytest
from services import asignacion_service as asg, catalogo_service as cat, estudiante_service as es, matricula_service as mat
from utils.excepciones import DuplicadoError, ValidacionError


def _ids(admin):
    g = lambda k: cat.opciones(admin, k)[0][0]
    return dict(id_anio=g("anios"), id_centro=g("centros"), id_grado=g("grados"), id_seccion=g("secciones"))


def test_matricula_duplicada(admin):
    e = es.crear(admin, {"codigo": "E-200", "nombres": "Nora Elena", "apellidos": "Mora Díaz", "sexo": "F"})["id"]
    mat.crear(admin, {**_ids(admin), "id_estudiante": e})
    with pytest.raises(DuplicadoError):
        mat.crear(admin, {**_ids(admin), "id_estudiante": e})


def test_asignacion_conflicto_de_horario(admin):
    existente = asg.listar(admin)[0]
    datos = {k: existente[k] for k in ("id_profesor", "id_centro", "id_anio", "id_grado", "id_seccion",
                                       "id_asignatura", "id_periodo", "id_modalidad", "dia_semana")}
    with pytest.raises(DuplicadoError):
        asg.crear(admin, datos)
    with pytest.raises(ValidacionError):
        asg.crear(admin, {**datos, "id_asignatura": None})


def test_catalogo_unico_y_eliminar_en_uso(admin):
    with pytest.raises(DuplicadoError):
        cat.crear(admin, "grados", {"nombre": "Séptimo", "orden": 7})
    grado = [g for g in cat.listar(admin, "grados") if g["nombre"] == "Séptimo"][0]
    with pytest.raises(ValidacionError):
        cat.eliminar(admin, "grados", grado["id"])
    with pytest.raises(ValidacionError):
        cat.crear(admin, "periodos", {"nombre": "P9", "hora_inicio": "10:00", "hora_fin": "09:00"})
