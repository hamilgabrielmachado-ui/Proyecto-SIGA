from datetime import date

from database.connection import get_session
from models import Asistencia, Estudiante, SesionAsistencia
from repositories.asignacion_repository import AsignacionRepository
from repositories.asistencia_repository import AsistenciaRepository
from repositories.matricula_repository import MatriculaRepository
from services import auditoria_service
from services._alcance import alcance, validar_asignacion_propia
from services.asignacion_service import _decorar
from services.permisos_service import requerir
from utils.constantes import AUSENTE, ESTADOS_ASISTENCIA, PRESENTE, TARDANZA
from utils.excepciones import ValidacionError


def asignaciones_disponibles(actor):
    """Asignaciones sobre las que el usuario puede registrar asistencia (docente: solo las suyas)."""
    requerir(actor, "asistencia.registrar")
    with get_session() as s:
        filas = AsignacionRepository(s).listar(id_profesor=None if actor.es_admin else actor.id_profesor)
    if not actor.es_admin and not actor.id_profesor:
        return []
    out = []
    for f in filas:
        _decorar(f)
        f["texto"] = (f"{f['grupo']} · {f['asignatura']} · {f['dia']} {f['periodo']}"
                      + (f" · {f['profesor']}" if actor.es_admin else ""))
        out.append(f)
    return out


def asignaciones_consultables(actor):
    """Para filtros de consulta: asignaciones visibles para el rol (el estudiante no las necesita)."""
    requerir(actor, "asistencia.consultar")
    if actor.es_estudiante:
        return []
    return asignaciones_disponibles(actor)


def cargar_lista(actor, id_asignacion, fecha: date):
    requerir(actor, "asistencia.registrar")
    with get_session() as s:
        asig = validar_asignacion_propia(s, actor, id_asignacion)
        estudiantes = MatriculaRepository(s).estudiantes_del_grupo(
            asig.id_anio, asig.id_centro, asig.id_grado, asig.id_seccion)
        repo = AsistenciaRepository(s)
        sesion = repo.sesion(id_asignacion, fecha)
        previos = repo.registros_de_sesion(sesion.id_sesion) if sesion else {}
        return {"existe": sesion is not None,
                "estudiantes": [{"id_estudiante": e.id_estudiante, "codigo": e.codigo,
                                 "nombre": f"{e.apellidos}, {e.nombres}",
                                 "estado": previos[e.id_estudiante].estado if e.id_estudiante in previos else PRESENTE,
                                 "observacion": (previos[e.id_estudiante].observacion or "")
                                 if e.id_estudiante in previos else ""} for e in estudiantes]}


def guardar(actor, id_asignacion, fecha: date, registros: list):
    """Crea la sesión y sus registros en una transacción. Si la sesión ya existe, la actualiza (sin duplicar)."""
    requerir(actor, "asistencia.registrar")
    if fecha is None or fecha > date.today():
        raise ValidacionError("La fecha de la sesión no puede ser futura.")
    if not registros:
        raise ValidacionError("No hay estudiantes matriculados en este grupo para registrar asistencia.")
    with get_session() as s:
        asig = validar_asignacion_propia(s, actor, id_asignacion)
        validos = {e.id_estudiante for e in MatriculaRepository(s).estudiantes_del_grupo(
            asig.id_anio, asig.id_centro, asig.id_grado, asig.id_seccion)}
        for r in registros:
            if r["id_estudiante"] not in validos:
                raise ValidacionError("La lista incluye un estudiante que no pertenece a este grupo.")
            if r["estado"] not in ESTADOS_ASISTENCIA:
                raise ValidacionError("Estado de asistencia no válido.")
            if len((r.get("observacion") or "")) > 200:
                raise ValidacionError("La observación admite máximo 200 caracteres.")
        if len({r["id_estudiante"] for r in registros}) != len(registros):
            raise ValidacionError("La lista contiene estudiantes repetidos.")
        repo = AsistenciaRepository(s)
        sesion = repo.sesion(id_asignacion, fecha)
        creada = sesion is None
        if creada:
            sesion = SesionAsistencia(id_asignacion=id_asignacion, fecha=fecha, id_usuario=actor.id_usuario)
            s.add(sesion)
            s.flush()
        previos = repo.registros_de_sesion(sesion.id_sesion)
        for r in registros:
            obs = (r.get("observacion") or "").strip() or None
            reg = previos.get(r["id_estudiante"])
            if reg:
                reg.estado, reg.observacion = r["estado"], obs
            else:
                s.add(Asistencia(id_sesion=sesion.id_sesion, id_estudiante=r["id_estudiante"],
                                 estado=r["estado"], observacion=obs))
        cuentas = {e: sum(1 for r in registros if r["estado"] == e) for e in ESTADOS_ASISTENCIA}
        auditoria_service.registrar(
            s, actor, "ASISTENCIA_REGISTRADA" if creada else "ASISTENCIA_MODIFICADA", "sesion_asistencia",
            sesion.id_sesion, f"asignación {id_asignacion}, fecha {fecha}, {cuentas}")
        return {"creada": creada, "presentes": cuentas[PRESENTE], "ausentes": cuentas[AUSENTE],
                "tardanzas": cuentas[TARDANZA]}


def consultar(actor, desde=None, hasta=None, id_asignacion=None, id_estudiante=None, estado=None, **filtros):
    """Consulta con alcance según el rol; los filtros del usuario nunca amplían el alcance."""
    requerir(actor, "asistencia.consultar")
    with get_session() as s:
        base = alcance(s, actor)
        extra = dict(filtros)
        if "id_asignaciones" in base:
            if id_asignacion:
                base["id_asignaciones"] = [i for i in base["id_asignaciones"] if i == id_asignacion]
        elif id_asignacion:
            extra["id_asignaciones"] = [id_asignacion]
        if "id_estudiante" not in base and id_estudiante:
            extra["id_estudiante"] = id_estudiante
        filas = AsistenciaRepository(s).consulta(desde=desde, hasta=hasta, estados=[estado] if estado else None,
                                                 **{**extra, **base})
    for f in filas:
        f["estudiante"] = f"{f['apellidos']}, {f['nombres']}"
        f["grupo"] = f"{f['grado']} {f['seccion']}"
        f["docente"] = f"{f['prof_apellidos']}, {f['prof_nombres']}"
        f["justificacion"] = f["just_estado"] or ("—" if f["estado"] == PRESENTE else "Sin justificar")
    return filas


def resumen(actor, desde=None, hasta=None):
    filas = consultar(actor, desde, hasta)
    r = {"total": len(filas), PRESENTE: 0, AUSENTE: 0, TARDANZA: 0}
    for f in filas:
        r[f["estado"]] += 1
    r["porcentaje"] = round((r[PRESENTE] + r[TARDANZA]) * 100 / r["total"], 1) if r["total"] else None
    return r
