"""Reportes de asistencia. Siempre respetan el alcance del rol (docente: solo sus grupos)."""
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from config import settings
from database.connection import get_session
from models import Grado, Profesor, Seccion
from repositories.asignacion_repository import AsignacionRepository
from repositories.matricula_repository import MatriculaRepository
from sqlalchemy import select
from services import asistencia_service, auditoria_service, justificacion_service
from services.permisos_service import requerir
from utils import exportacion
from utils.constantes import AUSENTE, PRESENTE, TARDANZA
from utils.excepciones import ValidacionError

# tipo -> (nombre, filtros requeridos, carpeta)
TIPOS = {
    "estudiante": ("Asistencia por estudiante", ["estudiante"], "estudiantes"),
    "grupo": ("Asistencia por grupo (asignación)", ["asignacion"], "asistencia"),
    "grado_seccion": ("Asistencia por grado y sección", ["grado", "seccion"], "asistencia"),
    "docente": ("Asistencia por docente", ["profesor"], "docentes"),
    "ausencias": ("Ausencias y tardanzas", [], "asistencia"),
    "justificaciones": ("Justificaciones", [], "asistencia"),
    "resumen_periodo": ("Resumen por periodo de clase", [], "asistencia"),
    "resumen_anio": ("Resumen por año lectivo", [], "asistencia"),
}


@dataclass
class Reporte:
    tipo: str
    titulo: str
    columnas: list = field(default_factory=list)
    filas: list = field(default_factory=list)
    resumen: str = ""


def opciones(actor):
    """Datos para los filtros, limitados al alcance del usuario."""
    requerir(actor, "reportes.generar")
    with get_session() as s:
        if actor.es_admin:
            profes = [(p.id_profesor, f"{p.apellidos}, {p.nombres}") for p in
                      s.scalars(select(Profesor).order_by(Profesor.apellidos))]
            from repositories.estudiante_repository import EstudianteRepository
            estudiantes = EstudianteRepository(s).buscar()
            asignaciones = AsignacionRepository(s).listar()
        else:
            p = s.get(Profesor, actor.id_profesor) if actor.id_profesor else None
            profes = [(p.id_profesor, p.nombre_completo)] if p else []
            estudiantes = MatriculaRepository(s).estudiantes_de_profesor(actor.id_profesor) if p else []
            asignaciones = AsignacionRepository(s).listar(id_profesor=actor.id_profesor) if p else []
        return {
            "profesores": profes,
            "estudiantes": [(e.id_estudiante, f"{e.apellidos}, {e.nombres} ({e.codigo})") for e in estudiantes],
            "asignaciones": [(a["id"], f"{a['grado']} {a['seccion']} · {a['asignatura']} · {a['periodo']}")
                             for a in asignaciones],
            "grados": [(g.id_grado, g.nombre) for g in s.scalars(select(Grado).order_by(Grado.orden))],
            "secciones": [(x.id_seccion, x.nombre) for x in s.scalars(select(Seccion).order_by(Seccion.nombre))],
        }


def _conteo(filas):
    c = {PRESENTE: 0, AUSENTE: 0, TARDANZA: 0}
    for f in filas:
        c[f["estado"]] += 1
    total = len(filas)
    pct = f"{(c[PRESENTE] + c[TARDANZA]) * 100 / total:.1f}%" if total else "—"
    return [c[PRESENTE], c[AUSENTE], c[TARDANZA], total, pct]


COLS_CONTEO = ["Presentes", "Ausentes", "Tardanzas", "Total", "% asistencia"]


def _agrupar(filas, clave, etiqueta_cols):
    grupos = defaultdict(list)
    for f in filas:
        grupos[clave(f)].append(f)
    return [list(k if isinstance(k, tuple) else (k,)) + _conteo(v) for k, v in sorted(grupos.items(), key=lambda x: str(x[0]))], \
        etiqueta_cols + COLS_CONTEO


def generar(actor, tipo, filtros: dict | None = None) -> Reporte:
    requerir(actor, "reportes.generar")
    if tipo not in TIPOS:
        raise ValidacionError("Seleccione un tipo de reporte válido.")
    flt = filtros or {}
    nombre, requeridos, _ = TIPOS[tipo]
    for r in requeridos:
        if not flt.get(r):
            raise ValidacionError(f"Seleccione «{r}» para generar este reporte.")
    desde, hasta = flt.get("desde"), flt.get("hasta")
    if desde and hasta and desde > hasta:
        raise ValidacionError("La fecha inicial no puede ser posterior a la fecha final.")
    filas = asistencia_service.consultar(
        actor, desde, hasta, id_asignacion=flt.get("asignacion"), id_estudiante=flt.get("estudiante"),
        id_profesor=flt.get("profesor"), id_grado=flt.get("grado"), id_seccion=flt.get("seccion"))
    rango = f" ({desde or 'inicio'} a {hasta or 'hoy'})"
    rep = Reporte(tipo, nombre + rango)

    if tipo == "estudiante":
        rep.columnas = ["Fecha", "Asignatura", "Periodo", "Estado", "Justificación", "Observación"]
        rep.filas = [[f["fecha"], f["asignatura"], f["periodo"], f["estado"], f["justificacion"],
                      f["observacion"] or ""] for f in filas]
    elif tipo in ("grupo", "grado_seccion"):
        rep.filas, rep.columnas = _agrupar(filas, lambda f: (f["codigo"], f["estudiante"]), ["Código", "Estudiante"])
    elif tipo == "docente":
        rep.filas, rep.columnas = _agrupar(filas, lambda f: (f["asignatura"], f["grupo"]), ["Asignatura", "Grupo"])
    elif tipo == "ausencias":
        rep.columnas = ["Fecha", "Estudiante", "Grupo", "Asignatura", "Periodo", "Estado", "Justificación"]
        rep.filas = [[f["fecha"], f["estudiante"], f["grupo"], f["asignatura"], f["periodo"], f["estado"],
                      f["justificacion"]] for f in filas if f["estado"] != PRESENTE]
    elif tipo == "justificaciones":
        just = [f for f in justificacion_service.listar(actor)
                if (not desde or f["fecha"] >= desde) and (not hasta or f["fecha"] <= hasta)]
        rep.columnas = ["Fecha", "Estudiante", "Grupo", "Asignatura", "Falta", "Motivo", "Estado"]
        rep.filas = [[f["fecha"], f["estudiante"], f["grupo"], f["asignatura"], f["estado"], f["motivo"],
                      f["estado_just"]] for f in just]
    elif tipo == "resumen_periodo":
        rep.filas, rep.columnas = _agrupar(filas, lambda f: f["periodo"], ["Periodo"])
    elif tipo == "resumen_anio":
        rep.filas, rep.columnas = _agrupar(filas, lambda f: f["anio"], ["Año lectivo"])
    rep.resumen = f"Registros considerados: {len(filas)}. % asistencia = (presentes + tardanzas) / total."
    return rep


def exportar(actor, reporte: Reporte, formato: str):
    """Guarda el reporte en reports/<categoria>/ con nombre normalizado y devuelve la ruta."""
    requerir(actor, "reportes.generar")
    if formato not in ("pdf", "xlsx"):
        raise ValidacionError("Formato de exportación no válido.")
    carpeta = settings.REPORTS_DIR / TIPOS[reporte.tipo][2]
    carpeta.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^a-z0-9]+", "_", reporte.tipo.lower())
    ruta = carpeta / f"{base}_{datetime.now():%Y%m%d_%H%M%S}.{formato}"
    (exportacion.exportar_pdf if formato == "pdf" else exportacion.exportar_excel)(reporte, ruta, actor.nombre)
    with get_session() as s:
        auditoria_service.registrar(s, actor, "REPORTE_GENERADO", "reporte", None, f"{reporte.tipo} → {ruta.name}")
    return ruta
