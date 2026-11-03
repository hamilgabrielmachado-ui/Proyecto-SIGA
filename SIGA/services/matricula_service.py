from datetime import date

from database.connection import get_session
from models import AnioLectivo, CentroEducativo, Estudiante, Grado, Matricula, Seccion
from repositories.matricula_repository import MatriculaRepository
from services import auditoria_service
from services.permisos_service import requerir
from utils.constantes import ESTADOS_MATRICULA
from utils.excepciones import DuplicadoError, NoEncontradoError, ValidacionError


def listar(actor, buscar="", id_anio=None, id_grado=None, id_seccion=None):
    requerir(actor, "matriculas.gestionar")
    with get_session() as s:
        filas = MatriculaRepository(s).listar(buscar, id_anio, id_grado, id_seccion)
    for f in filas:
        f["estudiante"] = f"{f['apellidos']}, {f['nombres']}"
    return filas


def _verificar_catalogos(s, d):
    pares = [(Estudiante, d["id_estudiante"], "estudiante"), (AnioLectivo, d["id_anio"], "año lectivo"),
             (CentroEducativo, d["id_centro"], "centro"), (Grado, d["id_grado"], "grado"),
             (Seccion, d["id_seccion"], "sección")]
    for modelo, id_, nombre in pares:
        if not id_:
            raise ValidacionError(f"Seleccione el {nombre}.")
        obj = s.get(modelo, id_)
        if obj is None:
            raise ValidacionError(f"El {nombre} seleccionado no existe.")
        if not obj.activo:
            raise ValidacionError(f"El {nombre} seleccionado está inactivo.")


def _normalizar(datos):
    estado = datos.get("estado") or "activa"
    if estado not in ESTADOS_MATRICULA:
        raise ValidacionError("El estado de la matrícula no es válido.")
    return {k: datos.get(k) for k in ("id_estudiante", "id_anio", "id_centro", "id_grado", "id_seccion")}, estado


def crear(actor, datos):
    requerir(actor, "matriculas.gestionar")
    d, estado = _normalizar(datos)
    with get_session() as s:
        _verificar_catalogos(s, d)
        repo = MatriculaRepository(s)
        if repo.existe(d["id_estudiante"], d["id_anio"]):
            raise DuplicadoError("El estudiante ya tiene una matrícula en ese año lectivo.")
        m = repo.agregar(Matricula(**d, estado=estado, fecha=date.today()))
        auditoria_service.registrar(s, actor, "MATRICULA_CREADA", "matricula", m.id_matricula,
                                    f"estudiante {m.id_estudiante}, año {m.id_anio}")
        return {"id": m.id_matricula}


def actualizar(actor, id_matricula, datos):
    """Permite cambiar centro, grado, sección y estado (no el estudiante ni el año)."""
    requerir(actor, "matriculas.gestionar")
    with get_session() as s:
        m = s.get(Matricula, id_matricula)
        if m is None:
            raise NoEncontradoError("La matrícula ya no existe.")
        d, estado = _normalizar({**datos, "id_estudiante": m.id_estudiante, "id_anio": m.id_anio})
        _verificar_catalogos(s, d)
        m.id_centro, m.id_grado, m.id_seccion, m.estado = d["id_centro"], d["id_grado"], d["id_seccion"], estado
        auditoria_service.registrar(s, actor, "MATRICULA_MODIFICADA", "matricula", m.id_matricula, estado)


def eliminar(actor, id_matricula):
    requerir(actor, "matriculas.gestionar")
    with get_session() as s:
        m = s.get(Matricula, id_matricula)
        if m is None:
            raise NoEncontradoError("La matrícula ya no existe.")
        s.delete(m)
        auditoria_service.registrar(s, actor, "MATRICULA_ELIMINADA", "matricula", id_matricula)
