from sqlalchemy.exc import IntegrityError

from database.connection import get_session
from models import CentroEducativo, Profesor, Turno
from repositories.profesor_repository import ProfesorRepository
from services import auditoria_service
from services._identidad import verificar_cedula_unica
from services.permisos_service import requerir
from utils.constantes import NIVELES_ACADEMICOS
from utils import validaciones as v
from utils.excepciones import DuplicadoError, NoEncontradoError, ValidacionError


def _fila(p):
    return {"id": p.id_profesor, "nombre": f"{p.apellidos}, {p.nombres}", "nombres": p.nombres,
            "apellidos": p.apellidos, "cedula": p.cedula, "codigo_mined": p.codigo_mined,
            "telefono": p.telefono or "", "especialidad": p.especialidad or "",
            "nivel_academico": p.nivel_academico or "", "id_centro": p.id_centro, "id_turno": p.id_turno,
            "centro": p.centro.nombre if p.centro else "", "turno": p.turno.nombre if p.turno else "",
            "anios_experiencia": p.anios_experiencia, "activo": p.activo}


def listar(actor, buscar="", activo=None):
    requerir(actor, "profesores.gestionar")
    with get_session() as s:
        return [_fila(p) for p in ProfesorRepository(s).buscar(buscar, activo)]


def opciones(actor, solo_activos=True):
    requerir(actor, "profesores.gestionar")
    with get_session() as s:
        return [(p.id_profesor, f"{p.apellidos}, {p.nombres}")
                for p in ProfesorRepository(s).buscar("", True if solo_activos else None)]


def _validar(datos):
    cedula = v.validar_cedula(datos.get("cedula"), requerida=True)
    nacimiento = v.fecha_de_cedula(cedula)
    edad = v.edad_en(nacimiento)
    if not v.EDAD_MIN_PROFESOR <= edad <= v.EDAD_MAX_PROFESOR:
        raise ValidacionError(f"La cédula corresponde a una persona de {edad} años; un profesor debe tener "
                              f"entre {v.EDAD_MIN_PROFESOR} y {v.EDAD_MAX_PROFESOR} años.")
    experiencia = v.entero_en_rango(datos.get("anios_experiencia") or 0, "Años de experiencia", 0, 60)
    if experiencia > edad - v.EDAD_MIN_PROFESOR:
        raise ValidacionError(f"Los años de experiencia ({experiencia}) no son posibles para una persona de "
                              f"{edad} años (máximo {max(edad - v.EDAD_MIN_PROFESOR, 0)}).")
    nivel = v.texto_opcional(datos.get("nivel_academico"), "Nivel académico", 50)
    if nivel and nivel not in NIVELES_ACADEMICOS:
        raise ValidacionError("Seleccione un nivel académico válido.")
    return {"nombres": v.validar_nombre_persona(datos.get("nombres"), "Nombres"),
            "apellidos": v.validar_nombre_persona(datos.get("apellidos"), "Apellidos"),
            "cedula": cedula,
            "codigo_mined": v.validar_codigo_mined(datos.get("codigo_mined")),
            "telefono": v.validar_telefono(datos.get("telefono")),
            "especialidad": v.validar_especialidad(datos.get("especialidad")),
            "nivel_academico": nivel,
            "id_centro": datos.get("id_centro") or None, "id_turno": datos.get("id_turno") or None,
            "anios_experiencia": experiencia,
            "activo": bool(datos.get("activo", True))}


def _verificar_referencias(s, d):
    for modelo, campo, nombre in ((CentroEducativo, "id_centro", "centro educativo"), (Turno, "id_turno", "turno")):
        if d[campo]:
            obj = s.get(modelo, d[campo])
            if obj is None or not obj.activo:
                raise ValidacionError(f"El {nombre} seleccionado no existe o está inactivo.")


def _duplicados(repo, d, id_actual=None):
    _verificar_referencias(repo.s, d)
    verificar_cedula_unica(repo.s, d["cedula"], id_profesor=id_actual)
    otro = repo.por_mined(d["codigo_mined"])
    if otro and otro.id_profesor != id_actual:
        raise DuplicadoError("Ya existe un profesor con ese código MINED.")


def crear(actor, datos):
    requerir(actor, "profesores.gestionar")
    d = _validar(datos)
    with get_session() as s:
        repo = ProfesorRepository(s)
        _duplicados(repo, d)
        p = repo.agregar(Profesor(**d))
        auditoria_service.registrar(s, actor, "PROFESOR_CREADO", "profesor", p.id_profesor, p.nombre_completo)
        return {"id": p.id_profesor}


def actualizar(actor, id_profesor, datos):
    requerir(actor, "profesores.gestionar")
    d = _validar(datos)
    with get_session() as s:
        repo = ProfesorRepository(s)
        p = repo.obtener(id_profesor)
        if p is None:
            raise NoEncontradoError("El profesor ya no existe.")
        _duplicados(repo, d, id_profesor)
        for k, val in d.items():
            setattr(p, k, val)
        auditoria_service.registrar(s, actor, "PROFESOR_MODIFICADO", "profesor", p.id_profesor, p.nombre_completo)


def eliminar(actor, id_profesor):
    requerir(actor, "profesores.gestionar")
    with get_session() as s:
        repo = ProfesorRepository(s)
        p = repo.obtener(id_profesor)
        if p is None:
            raise NoEncontradoError("El profesor ya no existe.")
        if repo.tiene_dependencias(id_profesor):
            raise ValidacionError("No se puede eliminar: el profesor tiene asignaciones o una cuenta de "
                                  "usuario. Puede desactivarlo en su lugar.")
        nombre = p.nombre_completo
        try:
            repo.eliminar(p)
        except IntegrityError:
            raise ValidacionError("No se puede eliminar: el registro está en uso.")
        auditoria_service.registrar(s, actor, "PROFESOR_ELIMINADO", "profesor", id_profesor, nombre)
