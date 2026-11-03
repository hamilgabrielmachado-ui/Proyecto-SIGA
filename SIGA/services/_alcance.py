"""Calcula qué datos puede ver cada rol. Se usa en los servicios de asistencia, justificaciones y reportes."""
from sqlalchemy import select

from models import AsignacionDocente
from utils.excepciones import PermisoError


def alcance(session, actor) -> dict:
    """Devuelve filtros para repository.consulta(): admin = todo, docente = sus grupos, estudiante = él mismo."""
    if actor.es_admin:
        return {}
    if actor.es_docente and actor.id_profesor:
        ids = session.scalars(select(AsignacionDocente.id_asignacion)
                              .where(AsignacionDocente.id_profesor == actor.id_profesor)).all()
        return {"id_asignaciones": ids}
    if actor.es_estudiante and actor.id_estudiante:
        return {"id_estudiante": actor.id_estudiante}
    raise PermisoError("Su cuenta no está vinculada a un profesor o estudiante.")


def validar_asignacion_propia(session, actor, id_asignacion):
    """Devuelve la asignación si el usuario puede trabajar con ella."""
    asig = session.get(AsignacionDocente, id_asignacion)
    if asig is None:
        from utils.excepciones import NoEncontradoError
        raise NoEncontradoError("La asignación seleccionada no existe.")
    if actor.es_admin:
        return asig
    if actor.es_docente and actor.id_profesor == asig.id_profesor:
        return asig
    raise PermisoError("No tiene permiso sobre este grupo.")
