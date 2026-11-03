"""Inicialización de la base: crea tablas que no existan y los datos base (idempotente).

IMPORTANTE: create_all() solo CREA tablas faltantes; no modifica tablas existentes.
Los cambios futuros de esquema deben hacerse con migraciones (ver database/migrations/README.md).
"""
from datetime import date

from sqlalchemy import select

import models  # noqa: F401  (registra las tablas)
from config import settings
from database.base import Base
from database.connection import engine, get_session
from models import (AnioLectivo, Grado, Modalidad, PeriodoClase, Permiso, Rol, Seccion, Turno, Usuario)
from utils import constantes as c
from utils.seguridad import generar_password_temporal, hash_password
from utils.validaciones import parsear_hora


def _sembrar_seguridad(s):
    permisos = {p.codigo: p for p in s.scalars(select(Permiso))}
    for codigo, desc in c.PERMISOS.items():
        if codigo not in permisos:
            permisos[codigo] = Permiso(codigo=codigo, descripcion=desc)
            s.add(permisos[codigo])
    roles = {r.nombre: r for r in s.scalars(select(Rol))}
    for nombre, codigos in c.PERMISOS_POR_ROL.items():
        rol = roles.get(nombre) or Rol(nombre=nombre, descripcion=f"Rol {nombre}")
        s.add(rol)
        rol.permisos = [permisos[cod] for cod in codigos]
        roles[nombre] = rol
    s.flush()
    return roles


def _sembrar_catalogos(s):
    def existe(modelo, **kw):
        return s.scalar(select(modelo).filter_by(**kw)) is not None
    for i, n in enumerate(c.GRADOS_INICIALES, start=7):
        if not existe(Grado, nombre=n):
            s.add(Grado(nombre=n, orden=i))
    for n in c.SECCIONES_INICIALES:
        if not existe(Seccion, nombre=n):
            s.add(Seccion(nombre=n))
    for n in c.MODALIDADES_INICIALES:
        if not existe(Modalidad, nombre=n):
            s.add(Modalidad(nombre=n))
    for n in c.TURNOS_INICIALES:
        if not existe(Turno, nombre=n):
            s.add(Turno(nombre=n))
    for n, ini, fin in c.PERIODOS_INICIALES:
        if not existe(PeriodoClase, nombre=n):
            s.add(PeriodoClase(nombre=n, hora_inicio=parsear_hora(ini), hora_fin=parsear_hora(fin)))
    if s.scalar(select(AnioLectivo)) is None:
        s.add(AnioLectivo(anio=date.today().year))


def _crear_admin(s, roles):
    """Crea el administrador inicial una sola vez. Devuelve la clave temporal si la generó."""
    if s.scalar(select(Usuario).where(Usuario.roles.any(Rol.nombre == c.ROL_ADMIN))):
        return None
    clave = settings.ADMIN_PASSWORD or generar_password_temporal(12)
    u = Usuario(username=settings.ADMIN_USER, password_hash=hash_password(clave), activo=True,
                debe_cambiar_password=True)
    u.roles.append(roles[c.ROL_ADMIN])
    s.add(u)
    return None if settings.ADMIN_PASSWORD else clave


def inicializar():
    """Prepara la base. Devuelve (usuario, clave_temporal) si se creó un administrador con clave generada."""
    Base.metadata.create_all(engine)
    with get_session() as s:
        roles = _sembrar_seguridad(s)
        _sembrar_catalogos(s)
        clave = _crear_admin(s, roles)
    return (settings.ADMIN_USER, clave) if clave else None


if __name__ == "__main__":
    nuevo = inicializar()
    print("Base de datos lista.")
    if nuevo:
        print(f"\n  Usuario administrador: {nuevo[0]}\n  Contraseña temporal : {nuevo[1]}\n"
            "  (Se le pedirá cambiarla al iniciar sesión. Anótela: no se volverá a mostrar.)")
