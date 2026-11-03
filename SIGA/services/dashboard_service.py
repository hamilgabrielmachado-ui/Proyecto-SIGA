"""Datos de los paneles iniciales. Todo proviene de la base de datos."""
from datetime import date, timedelta

from sqlalchemy import func, select

from database.connection import get_session
from models import Estudiante, Justificacion, Matricula, Profesor
from repositories.catalogo_repository import CatalogoRepository
from services import asignacion_service, asistencia_service
from services._alcance import alcance
from services.permisos_service import requerir_autenticado
from utils.constantes import PENDIENTE


def _pendientes(actor):
    from services import justificacion_service
    return len(justificacion_service.listar(actor, PENDIENTE))


def admin(actor):
    requerir_autenticado(actor)
    with get_session() as s:
        anio = CatalogoRepository(s).anio_actual()
        n_est = s.scalar(select(func.count()).select_from(Estudiante).where(Estudiante.activo.is_(True)))
        n_prof = s.scalar(select(func.count()).select_from(Profesor).where(Profesor.activo.is_(True)))
        q = select(func.count()).select_from(Matricula).where(Matricula.estado == "activa")
        if anio:
            q = q.where(Matricula.id_anio == anio.id_anio)
        n_mat = s.scalar(q)
    res = asistencia_service.resumen(actor, date.today() - timedelta(days=30), date.today())
    return {"estudiantes": n_est, "profesores": n_prof, "matriculas": n_mat,
            "anio": anio.anio if anio else None, "asistencia": res, "pendientes": _pendientes(actor)}


def docente(actor):
    requerir_autenticado(actor)
    hoy = asignacion_service.mi_horario(actor, solo_hoy=True)
    todas = asignacion_service.mi_horario(actor)
    grupos = {(f["grupo"], f["asignatura"]) for f in todas}
    res = asistencia_service.resumen(actor, date.today() - timedelta(days=30), date.today())
    return {"nombre": actor.nombre, "grupos": len(grupos), "clases_hoy": hoy, "asistencia": res,
            "pendientes": _pendientes(actor)}


def estudiante(actor):
    requerir_autenticado(actor)
    with get_session() as s:
        from repositories.matricula_repository import MatriculaRepository
        m = MatriculaRepository(s).matricula_activa(actor.id_estudiante) if actor.id_estudiante else None
        grupo = None
        if m:
            from models import Grado, Seccion
            grupo = f"{s.get(Grado, m.id_grado).nombre} {s.get(Seccion, m.id_seccion).nombre}"
    return {"nombre": actor.nombre, "grupo": grupo, "clases_hoy": asignacion_service.mi_horario(actor, True),
            "asistencia": asistencia_service.resumen(actor), "pendientes": _pendientes(actor)}
