from sqlalchemy.exc import IntegrityError

from database.connection import get_session
from models import Estudiante
from repositories.estudiante_repository import EstudianteRepository
from services import auditoria_service
from services._identidad import verificar_cedula_unica
from services.permisos_service import requerir
from utils.excepciones import DuplicadoError, NoEncontradoError, ValidacionError
from utils.constantes import SEXOS
from utils import validaciones as v


def _fila(e):
    return {"id": e.id_estudiante, "codigo": e.codigo, "nombre": f"{e.apellidos}, {e.nombres}",
            "nombres": e.nombres, "apellidos": e.apellidos, "cedula": e.cedula or "",
            "fecha_nacimiento": e.fecha_nacimiento, "sexo": e.sexo, "telefono": e.telefono or "",
            "correo": e.correo or "", "activo": e.activo}


def listar(actor, buscar="", activo=None):
    requerir(actor, "estudiantes.gestionar")
    with get_session() as s:
        return [_fila(e) for e in EstudianteRepository(s).buscar(buscar, activo)]


def opciones(actor, solo_activos=True):
    requerir(actor, "estudiantes.gestionar")
    with get_session() as s:
        return [(e.id_estudiante, f"{e.apellidos}, {e.nombres} ({e.codigo})")
                for e in EstudianteRepository(s).buscar("", True if solo_activos else None)]


def _validar(datos):
    sexo = (datos.get("sexo") or "").strip()
    if sexo not in SEXOS:
        raise ValidacionError("Seleccione el sexo del estudiante.")
    nombres = v.validar_nombre_persona(datos.get("nombres"), "Nombres")
    apellidos = v.validar_nombre_persona(datos.get("apellidos"), "Apellidos")
    v.validar_sexo_con_nombre(sexo, nombres)
    cedula = v.validar_cedula(datos.get("cedula"))
    nacimiento = v.validar_fecha_nacimiento(datos.get("fecha_nacimiento"), "Fecha de nacimiento",
                                            v.EDAD_MIN_ESTUDIANTE, v.EDAD_MAX_ESTUDIANTE)
    if cedula and nacimiento is None:
        nacimiento = v.fecha_de_cedula(cedula)      # la cédula ya contiene la fecha de nacimiento
    v.validar_cedula_con_fecha(cedula, nacimiento)
    return {"codigo": v.validar_codigo_alfanumerico(datos.get("codigo"), "Código estudiantil"),
            "cedula": cedula, "nombres": nombres, "apellidos": apellidos,
            "fecha_nacimiento": nacimiento, "sexo": sexo,
            "telefono": v.validar_telefono(datos.get("telefono")),
            "correo": v.validar_correo(datos.get("correo")),
            "activo": bool(datos.get("activo", True))}


def _verificar_duplicados(repo, d, id_actual=None):
    otro = repo.por_codigo(d["codigo"])
    if otro and otro.id_estudiante != id_actual:
        raise DuplicadoError("Ya existe un estudiante con ese código estudiantil.")
    verificar_cedula_unica(repo.s, d["cedula"], id_estudiante=id_actual)
    if d["correo"]:
        otro = repo.por_correo(d["correo"])
        if otro and otro.id_estudiante != id_actual:
            raise DuplicadoError("Ya existe un estudiante con ese correo electrónico.")


def crear(actor, datos):
    requerir(actor, "estudiantes.gestionar")
    d = _validar(datos)
    with get_session() as s:
        repo = EstudianteRepository(s)
        _verificar_duplicados(repo, d)
        e = repo.agregar(Estudiante(**d))
        auditoria_service.registrar(s, actor, "ESTUDIANTE_CREADO", "estudiante", e.id_estudiante,
                                    f"{e.codigo} {e.nombre_completo}")
        return {"id": e.id_estudiante}


def actualizar(actor, id_estudiante, datos):
    requerir(actor, "estudiantes.gestionar")
    d = _validar(datos)
    with get_session() as s:
        repo = EstudianteRepository(s)
        e = repo.obtener(id_estudiante)
        if e is None:
            raise NoEncontradoError("El estudiante ya no existe.")
        _verificar_duplicados(repo, d, id_estudiante)
        for k, val in d.items():
            setattr(e, k, val)
        auditoria_service.registrar(s, actor, "ESTUDIANTE_MODIFICADO", "estudiante", e.id_estudiante,
                                    f"{e.codigo} {e.nombre_completo}")


def eliminar(actor, id_estudiante):
    requerir(actor, "estudiantes.gestionar")
    with get_session() as s:
        repo = EstudianteRepository(s)
        e = repo.obtener(id_estudiante)
        if e is None:
            raise NoEncontradoError("El estudiante ya no existe.")
        if repo.tiene_dependencias(id_estudiante):
            raise ValidacionError("No se puede eliminar: el estudiante tiene matrículas, asistencia o una "
                                "cuenta asociada. Puede desactivarlo en su lugar.")
        detalle = f"{e.codigo} {e.nombre_completo}"
        try:
            repo.eliminar(e)
        except IntegrityError:
            raise ValidacionError("No se puede eliminar: el registro está en uso.")
        auditoria_service.registrar(s, actor, "ESTUDIANTE_ELIMINADO", "estudiante", id_estudiante, detalle)
