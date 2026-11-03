import re
from datetime import date, time

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.connection import get_session
from repositories.catalogo_repository import DEFINICIONES, CatalogoRepository, pk_nombre
from services import auditoria_service
from services.permisos_service import requerir, requerir_autenticado
from utils import validaciones as v
from utils.excepciones import DuplicadoError, NoEncontradoError, ValidacionError


def definiciones():
    return DEFINICIONES


def _etiqueta(clave, o):
    if clave == "periodos":
        return f"{o.nombre} ({o.hora_inicio:%H:%M}-{o.hora_fin:%H:%M})"
    if clave == "anios":
        return str(o.anio)
    return o.nombre


def _fila(clave, o):
    d = DEFINICIONES[clave]
    fila = {"id": getattr(o, pk_nombre(d.modelo)), "activo": o.activo}
    for attr, _, tipo, _ in d.campos:
        val = getattr(o, attr)
        fila[attr] = val.strftime("%H:%M") if tipo == "hora" and val else ("" if val is None else val)
    return fila


def listar(actor, clave, buscar=""):
    requerir(actor, "catalogos.gestionar")
    with get_session() as s:
        filas = [_fila(clave, o) for o in CatalogoRepository(s).listar(clave)]
    if buscar:
        b = buscar.lower()
        filas = [f for f in filas if any(b in str(val).lower() for val in f.values())]
    return filas


def opciones(actor, clave, solo_activos=True):
    """Lista (id, texto) para listas desplegables. Disponible para cualquier usuario autenticado."""
    requerir_autenticado(actor)
    with get_session() as s:
        d = DEFINICIONES[clave]
        return [(getattr(o, pk_nombre(d.modelo)), _etiqueta(clave, o))
                for o in CatalogoRepository(s).listar(clave, solo_activos)]


def anio_actual(actor):
    requerir_autenticado(actor)
    with get_session() as s:
        a = CatalogoRepository(s).anio_actual()
        return (a.id_anio, a.anio) if a else None


def _validar_texto(clave, attr, etiqueta, val, requerido):
    """Regla de cada campo de texto según el catálogo."""
    if attr == "nombre":
        if clave == "periodos":
            return v.texto_con_numeros(val, etiqueta, requerido, minimo=3, maximo=100)
        if clave == "secciones":
            letra = v.texto_requerido(val, etiqueta, 1).upper()
            if not re.fullmatch(r"[A-Z]", letra):
                raise ValidacionError("La sección debe ser una sola letra (A, B, C…).")
            return letra
        return v.solo_texto(val, etiqueta, requerido, minimo=3, maximo=150)
    if attr == "codigo":
        return v.validar_codigo_alfanumerico(val, etiqueta, requerido, minimo=2, maximo=30)
    if attr == "direccion":
        return v.validar_direccion(val, etiqueta, requerido, minimo=5, maximo=200)
    return v.texto_requerido(val, etiqueta, 150) if requerido else v.texto_opcional(val, etiqueta, 200)


def _validar(clave, datos):
    d = DEFINICIONES[clave]
    limpio = {}
    for attr, etiqueta, tipo, requerido in d.campos:
        val = datos.get(attr)
        if tipo == "texto":
            limpio[attr] = _validar_texto(clave, attr, etiqueta, val, requerido)
        elif tipo == "entero":
            rango = (2000, date.today().year + 1) if clave == "anios" else (1, 12)
            limpio[attr] = v.entero_en_rango(val, etiqueta, *rango, requerido=requerido)
        elif tipo == "hora":
            limpio[attr] = v.parsear_hora(val, etiqueta)
    if clave == "periodos":
        ini, fin = limpio["hora_inicio"], limpio["hora_fin"]
        if fin <= ini:
            raise ValidacionError("La hora de fin debe ser posterior a la hora de inicio.")
        if not (time(5, 0) <= ini and fin <= time(22, 0)):
            raise ValidacionError("El periodo debe estar dentro del horario escolar (05:00 a 22:00).")
        minutos = (fin.hour * 60 + fin.minute) - (ini.hour * 60 + ini.minute)
        if not 20 <= minutos <= 240:
            raise ValidacionError("Un periodo de clase debe durar entre 20 minutos y 4 horas.")
    limpio["activo"] = bool(datos.get("activo", True))
    return limpio


def _verificar_unico(repo, clave, limpio, id_actual=None):
    d = DEFINICIONES[clave]
    pk = pk_nombre(d.modelo)
    otro = repo.por_unico(clave, limpio[d.unico])
    if otro and getattr(otro, pk) != id_actual:
        raise DuplicadoError(f"Ya existe un registro con ese valor en «{d.etiqueta}».")
    if limpio.get("codigo"):                       # el código de centros y asignaturas no se repite
        otro = repo.s.scalar(select(d.modelo).where(d.modelo.codigo == limpio["codigo"]))
        if otro and getattr(otro, pk) != id_actual:
            raise DuplicadoError("Ya existe un registro con ese código.")


def crear(actor, clave, datos):
    requerir(actor, "catalogos.gestionar")
    limpio = _validar(clave, datos)
    with get_session() as s:
        repo = CatalogoRepository(s)
        _verificar_unico(repo, clave, limpio)
        o = repo.agregar(DEFINICIONES[clave].modelo(**limpio))
        auditoria_service.registrar(s, actor, "CATALOGO_CREADO", clave, getattr(o, pk_nombre(type(o))))


def actualizar(actor, clave, id_, datos):
    requerir(actor, "catalogos.gestionar")
    limpio = _validar(clave, datos)
    with get_session() as s:
        repo = CatalogoRepository(s)
        o = repo.obtener_de(clave, id_)
        if o is None:
            raise NoEncontradoError("El registro ya no existe.")
        _verificar_unico(repo, clave, limpio, id_)
        for k, val in limpio.items():
            setattr(o, k, val)
        auditoria_service.registrar(s, actor, "CATALOGO_MODIFICADO", clave, id_)


def eliminar(actor, clave, id_):
    requerir(actor, "catalogos.gestionar")
    with get_session() as s:
        repo = CatalogoRepository(s)
        o = repo.obtener_de(clave, id_)
        if o is None:
            raise NoEncontradoError("El registro ya no existe.")
        try:
            repo.eliminar(o)
        except IntegrityError:
            s.rollback()
            raise ValidacionError("No se puede eliminar: el elemento está en uso por otros registros "
                                  "(matrículas, asignaciones, profesores…). Desactívelo en su lugar.")
        auditoria_service.registrar(s, actor, "CATALOGO_ELIMINADO", clave, id_)
