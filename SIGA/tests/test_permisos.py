import pytest
from services import (asistencia_service, estudiante_service, matricula_service, usuario_service,
                      reportes_service, auditoria_service)
from utils.excepciones import PermisoError


def test_docente_no_gestiona_usuarios_ni_estudiantes(docente):
    for fn in (lambda: usuario_service.listar(docente), lambda: estudiante_service.listar(docente),
               lambda: matricula_service.listar(docente), lambda: auditoria_service.listar(docente)):
        with pytest.raises(PermisoError):
            fn()


def test_estudiante_no_registra_asistencia_ni_reportes(estudiante):
    with pytest.raises(PermisoError):
        asistencia_service.asignaciones_disponibles(estudiante)
    with pytest.raises(PermisoError):
        reportes_service.generar(estudiante, "ausencias")


def test_docente_no_accede_a_grupo_ajeno(db, docente, admin):
    from datetime import date
    from services import asignacion_service as asg
    from database.connection import get_session
    from models import AsignacionDocente, Profesor
    with get_session() as s:
        otro = Profesor(nombres="Otro", apellidos="Prof", cedula="X-123456", codigo_mined="M-9")
        s.add(otro); s.flush()
        base = s.query(AsignacionDocente).first()
        ajena = AsignacionDocente(id_profesor=otro.id_profesor, id_centro=base.id_centro, id_anio=base.id_anio,
                                  id_grado=base.id_grado, id_seccion=base.id_seccion + 1 if False else base.id_seccion,
                                  id_asignatura=base.id_asignatura, id_periodo=base.id_periodo + 1,
                                  id_modalidad=base.id_modalidad, dia_semana=1)
        s.add(ajena); s.flush()
        id_ajena = ajena.id_asignacion
    with pytest.raises(PermisoError):
        asistencia_service.cargar_lista(docente, id_ajena, date.today())
    with pytest.raises(PermisoError):
        asistencia_service.guardar(docente, id_ajena, date.today(), [{"id_estudiante": 1, "estado": "presente"}])
    # el administrador sí puede
    assert asistencia_service.cargar_lista(admin, id_ajena, date.today())["estudiantes"]
