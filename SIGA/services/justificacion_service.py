from datetime import datetime

from database.connection import get_session
from models import Justificacion
from repositories.asistencia_repository import AsistenciaRepository
from repositories.justificacion_repository import JustificacionRepository
from services import auditoria_service
from services._alcance import alcance
from services.permisos_service import requerir
from utils.constantes import APROBADA, AUSENTE, PENDIENTE, PRESENTE, RECHAZADA, TARDANZA
from utils.excepciones import DuplicadoError, NoEncontradoError, PermisoError, ValidacionError


def _decorar(f):
    f["estudiante"] = f"{f['apellidos']}, {f['nombres']}"
    f["grupo"] = f"{f['grado']} {f['seccion']}"
    f["id"] = f["id_justificacion"]
    f["estado_just"] = f["just_estado"]
    return f


def listar(actor, estado=None):
    requerir(actor, "justificaciones.consultar")
    with get_session() as s:
        base = alcance(s, actor)
        filas = AsistenciaRepository(s).consulta(solo_justificadas=True, estado_just=estado, **base)
    return [_decorar(f) for f in filas]


def ausencias_sin_justificar(actor):
    requerir(actor, "justificaciones.registrar")
    with get_session() as s:
        base = alcance(s, actor)
        filas = AsistenciaRepository(s).consulta(estados=[AUSENTE, TARDANZA], **base)
    out = []
    for f in filas:
        if f["id_justificacion"] is None:
            f["estudiante"] = f"{f['apellidos']}, {f['nombres']}"
            f["texto"] = (f"{f['fecha']} · {f['estudiante']} · {f['asignatura']} · {f['estado']}")
            out.append(f)
    return out


def registrar(actor, id_asistencia, motivo):
    requerir(actor, "justificaciones.registrar")
    motivo = (motivo or "").strip()
    if len(motivo) < 5:
        raise ValidacionError("Escriba el motivo de la justificación (al menos 5 caracteres).")
    if len(motivo) > 500:
        raise ValidacionError("El motivo admite máximo 500 caracteres.")
    with get_session() as s:
        filas = AsistenciaRepository(s).consulta(id_asistencia=id_asistencia, **alcance(s, actor))
        if not filas:
            raise PermisoError("No tiene permiso sobre este registro de asistencia o no existe.")
        if filas[0]["estado"] == PRESENTE:
            raise ValidacionError("Solo se pueden justificar ausencias o tardanzas.")
        repo = JustificacionRepository(s)
        if repo.por_asistencia(id_asistencia):
            raise DuplicadoError("Este registro ya tiene una justificación.")
        j = repo.agregar(Justificacion(id_asistencia=id_asistencia, motivo=motivo, estado=PENDIENTE,
                                       id_solicitante=actor.id_usuario))
        auditoria_service.registrar(s, actor, "JUSTIFICACION_REGISTRADA", "justificacion", j.id_justificacion)
        return {"id": j.id_justificacion}


def resolver(actor, id_justificacion, aprobar: bool, comentario=""):
    requerir(actor, "justificaciones.revisar")
    comentario = (comentario or "").strip()
    if not aprobar and not comentario:
        raise ValidacionError("Indique el motivo del rechazo en el comentario.")
    with get_session() as s:
        filas = AsistenciaRepository(s).consulta(id_justificacion=id_justificacion, **alcance(s, actor))
        if not filas:
            raise PermisoError("No tiene permiso sobre esta justificación o no existe.")
        j = s.get(Justificacion, id_justificacion)
        if j is None:
            raise NoEncontradoError("La justificación ya no existe.")
        if j.estado != PENDIENTE:
            raise ValidacionError("Esta justificación ya fue revisada.")
        j.estado = APROBADA if aprobar else RECHAZADA
        j.id_revisor, j.fecha_revision = actor.id_usuario, datetime.now()
        j.comentario_revision = comentario[:300] or None
        auditoria_service.registrar(s, actor, "JUSTIFICACION_APROBADA" if aprobar else "JUSTIFICACION_RECHAZADA",
                                    "justificacion", j.id_justificacion, comentario[:200] or None)
