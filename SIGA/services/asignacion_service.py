from datetime import date

from sqlalchemy.exc import IntegrityError

from database.connection import get_session
from models import (AnioLectivo, AsignacionDocente, Asignatura, CentroEducativo, Grado, Modalidad,
                    PeriodoClase, Profesor, Seccion, SesionAsistencia)
from repositories.asignacion_repository import AsignacionRepository
from repositories.catalogo_repository import CatalogoRepository
from repositories.matricula_repository import MatriculaRepository
from services import auditoria_service
from services.permisos_service import requerir, requerir_autenticado
from utils.constantes import DIAS_SEMANA
from utils.excepciones import DuplicadoError, NoEncontradoError, PermisoError, ValidacionError

CAMPOS = ("id_profesor", "id_centro", "id_anio", "id_grado", "id_seccion", "id_asignatura",
          "id_periodo", "id_modalidad", "dia_semana")


def _decorar(f):
    f["profesor"] = f"{f['prof_apellidos']}, {f['prof_nombres']}"
    f["grupo"] = f"{f['grado']} {f['seccion']}"
    f["dia"] = DIAS_SEMANA.get(f["dia_semana"], "")
    f["horario"] = f"{f['hora_inicio']:%H:%M}-{f['hora_fin']:%H:%M}"
    return f


def listar(actor, buscar=""):
    requerir(actor, "asignaciones.gestionar")
    with get_session() as s:
        return [_decorar(f) for f in AsignacionRepository(s).listar(buscar=buscar)]


def _validar(s, d):
    for c in CAMPOS:
        if not d.get(c):
            raise ValidacionError("Complete todos los campos de la asignación.")
    if d["dia_semana"] not in DIAS_SEMANA:
        raise ValidacionError("El día de la semana no es válido.")
    if d["dia_semana"] == 7:
        raise ValidacionError("No se asignan clases los domingos.")
    for modelo, c, nombre in [(Profesor, "id_profesor", "profesor"), (CentroEducativo, "id_centro", "centro"),
                              (AnioLectivo, "id_anio", "año lectivo"), (Grado, "id_grado", "grado"),
                              (Seccion, "id_seccion", "sección"), (Asignatura, "id_asignatura", "asignatura"),
                              (PeriodoClase, "id_periodo", "periodo"), (Modalidad, "id_modalidad", "modalidad")]:
        obj = s.get(modelo, d[c])
        if obj is None or not obj.activo:
            raise ValidacionError(f"El {nombre} seleccionado no existe o está inactivo.")


def _conflictos(repo, d, excluir=None):
    if repo.conflicto_profesor(d, excluir):
        raise DuplicadoError("El profesor ya tiene una clase asignada en ese día y periodo.")
    if repo.conflicto_grupo(d, excluir):
        raise DuplicadoError("Ese grupo ya tiene una clase asignada en ese día y periodo.")


def crear(actor, datos):
    requerir(actor, "asignaciones.gestionar")
    d = {c: datos.get(c) for c in CAMPOS}
    with get_session() as s:
        _validar(s, d)
        repo = AsignacionRepository(s)
        _conflictos(repo, d)
        a = repo.agregar(AsignacionDocente(**d))
        auditoria_service.registrar(s, actor, "ASIGNACION_CREADA", "asignacion_docente", a.id_asignacion)
        return {"id": a.id_asignacion}


def actualizar(actor, id_asignacion, datos):
    requerir(actor, "asignaciones.gestionar")
    d = {c: datos.get(c) for c in CAMPOS}
    with get_session() as s:
        a = s.get(AsignacionDocente, id_asignacion)
        if a is None:
            raise NoEncontradoError("La asignación ya no existe.")
        _validar(s, d)
        _conflictos(AsignacionRepository(s), d, id_asignacion)
        for k, val in d.items():
            setattr(a, k, val)
        auditoria_service.registrar(s, actor, "ASIGNACION_MODIFICADA", "asignacion_docente", id_asignacion)


def eliminar(actor, id_asignacion):
    requerir(actor, "asignaciones.gestionar")
    with get_session() as s:
        a = s.get(AsignacionDocente, id_asignacion)
        if a is None:
            raise NoEncontradoError("La asignación ya no existe.")
        if s.query(SesionAsistencia).filter_by(id_asignacion=id_asignacion).first():
            raise ValidacionError("No se puede eliminar: ya existe asistencia registrada para esta asignación.")
        try:
            s.delete(a)
            s.flush()
        except IntegrityError:
            raise ValidacionError("No se puede eliminar: la asignación está en uso.")
        auditoria_service.registrar(s, actor, "ASIGNACION_ELIMINADA", "asignacion_docente", id_asignacion)


def mi_horario(actor, solo_hoy=False):
    """Horario del docente (sus asignaciones) o del estudiante (clases de su grupo)."""
    requerir(actor, "asignaciones.consultar")
    dia = date.today().isoweekday() if solo_hoy else None
    with get_session() as s:
        repo = AsignacionRepository(s)
        if actor.es_docente and actor.id_profesor:
            anio = CatalogoRepository(s).anio_actual()
            filas = repo.listar(id_profesor=actor.id_profesor, id_anio=anio.id_anio if anio else None, dia=dia)
        elif actor.es_estudiante and actor.id_estudiante:
            m = MatriculaRepository(s).matricula_activa(actor.id_estudiante)
            if not m:
                return []
            filas = repo.listar(dia=dia, grupo=(m.id_anio, m.id_centro, m.id_grado, m.id_seccion))
        elif actor.es_admin:
            raise PermisoError("El administrador consulta las asignaciones desde el módulo de asignaciones.")
        else:
            raise PermisoError("Su cuenta no está vinculada a un profesor o estudiante.")
        return [_decorar(f) for f in filas]
