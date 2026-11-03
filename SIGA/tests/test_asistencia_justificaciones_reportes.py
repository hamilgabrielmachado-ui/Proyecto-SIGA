from datetime import date, timedelta

import pytest
from services import (asistencia_service as asi, justificacion_service as jus, reportes_service as rep,
                      asignacion_service as asg, usuario_service)
from utils.excepciones import PermisoError, ValidacionError


def _registrar(docente, estados):
    a = asi.asignaciones_disponibles(docente)[0]
    lista = asi.cargar_lista(docente, a["id"], date.today())
    regs = [{"id_estudiante": e["id_estudiante"], "estado": estados[i % len(estados)], "observacion": ""}
            for i, e in enumerate(lista["estudiantes"])]
    return a, asi.guardar(docente, a["id"], date.today(), regs)


def test_guardar_asistencia_no_duplica(docente):
    a, r = _registrar(docente, ["presente", "ausente", "tardanza"])
    assert r["creada"] and r["ausentes"] == 2
    _, r2 = _registrar(docente, ["presente"])
    assert r2["creada"] is False
    assert len(asi.consultar(docente)) == 6


def test_no_acepta_fecha_futura_ni_estado_invalido(docente):
    a = asi.asignaciones_disponibles(docente)[0]
    with pytest.raises(ValidacionError):
        asi.guardar(docente, a["id"], date.today() + timedelta(days=1), [{"id_estudiante": 1, "estado": "presente"}])
    with pytest.raises(ValidacionError):
        asi.guardar(docente, a["id"], date.today(), [{"id_estudiante": 999, "estado": "presente"}])


def test_estudiante_solo_ve_su_asistencia(docente, estudiante):
    _registrar(docente, ["ausente"])
    filas = asi.consultar(estudiante)
    assert len(filas) == 1 and filas[0]["codigo"] == "E-001"
    # intentar pedir a otro estudiante no amplía el alcance
    assert len(asi.consultar(estudiante, id_estudiante=999)) == 1


def test_flujo_justificacion(docente, estudiante, admin):
    _registrar(docente, ["ausente"])
    pendientes = jus.ausencias_sin_justificar(docente)
    assert len(pendientes) == 6
    jus.registrar(docente, pendientes[0]["id_asistencia"], "Cita médica")
    with pytest.raises(Exception):
        jus.registrar(docente, pendientes[0]["id_asistencia"], "Otra vez")
    j = jus.listar(docente, "pendiente")[0]
    with pytest.raises(ValidacionError):
        jus.resolver(docente, j["id"], False, "")
    jus.resolver(docente, j["id"], True, "Comprobante presentado")
    assert jus.listar(admin, "aprobada")
    with pytest.raises(PermisoError):
        jus.resolver(estudiante, j["id"], True)


def test_reportes_y_exportacion(docente, admin, tmp_path, monkeypatch):
    from config import settings
    monkeypatch.setattr(settings, "REPORTS_DIR", tmp_path)
    _registrar(docente, ["presente", "ausente"])
    opc = rep.opciones(docente)
    r = rep.generar(docente, "grupo", {"asignacion": opc["asignaciones"][0][0]})
    assert r.filas and r.columnas[-1] == "% asistencia"
    for tipo in rep.TIPOS:
        filtros = {"asignacion": opc["asignaciones"][0][0], "estudiante": opc["estudiantes"][0][0],
                   "grado": opc["grados"][0][0], "seccion": opc["secciones"][0][0],
                   "profesor": opc["profesores"][0][0]}
        assert rep.generar(admin, tipo, filtros) is not None
    for fmt in ("pdf", "xlsx"):
        assert rep.exportar(docente, r, fmt).exists()


def test_horario_y_auditoria(docente, estudiante, admin):
    from services import auditoria_service
    assert asg.mi_horario(docente) and asg.mi_horario(estudiante)
    assert any(a["accion"] == "LOGIN" for a in auditoria_service.listar(admin))


def test_usuarios_admin(admin):
    with pytest.raises(ValidacionError):
        usuario_service.crear(admin, {"username": "x", "password": "Clave1234", "rol": "Docente"})
    t = usuario_service.restablecer_password(admin, [u for u in usuario_service.listar(admin) if u["username"] == "docente"][0]["id"])
    assert len(t) >= 8
