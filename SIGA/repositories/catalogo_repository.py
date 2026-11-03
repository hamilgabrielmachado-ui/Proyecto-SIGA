"""Acceso genérico a los catálogos académicos (centros, grados, secciones, etc.)."""
from dataclasses import dataclass, field

from sqlalchemy import inspect, select

from models import (AnioLectivo, Asignatura, CentroEducativo, Grado, Modalidad,
                    PeriodoClase, Seccion, Turno)
from repositories.base_repository import BaseRepository


@dataclass
class DefCatalogo:
    clave: str
    etiqueta: str
    modelo: type
    campos: list = field(default_factory=list)   # (atributo, etiqueta, tipo, requerido)
    unico: str = "nombre"
    orden: str = "nombre"


DEFINICIONES = {d.clave: d for d in [
    DefCatalogo("centros", "Centros educativos", CentroEducativo,
                [("nombre", "Nombre", "texto", True), ("codigo", "Código", "texto", False),
                 ("direccion", "Dirección", "texto", False)]),
    DefCatalogo("grados", "Grados", Grado,
                [("nombre", "Nombre", "texto", True), ("orden", "Orden", "entero", True)], orden="orden"),
    DefCatalogo("secciones", "Secciones", Seccion, [("nombre", "Nombre", "texto", True)]),
    DefCatalogo("asignaturas", "Asignaturas", Asignatura,
                [("nombre", "Nombre", "texto", True), ("codigo", "Código", "texto", False)]),
    DefCatalogo("turnos", "Turnos", Turno, [("nombre", "Nombre", "texto", True)]),
    DefCatalogo("modalidades", "Modalidades", Modalidad, [("nombre", "Nombre", "texto", True)]),
    DefCatalogo("periodos", "Periodos de clase", PeriodoClase,
                [("nombre", "Nombre", "texto", True), ("hora_inicio", "Hora inicio (HH:MM)", "hora", True),
                 ("hora_fin", "Hora fin (HH:MM)", "hora", True)], orden="hora_inicio"),
    DefCatalogo("anios", "Años lectivos", AnioLectivo, [("anio", "Año", "entero", True)],
                unico="anio", orden="anio"),
]}


def pk_nombre(modelo) -> str:
    return inspect(modelo).primary_key[0].key


class CatalogoRepository(BaseRepository):
    def definicion(self, clave) -> DefCatalogo:
        return DEFINICIONES[clave]

    def listar(self, clave, solo_activos=False):
        d = DEFINICIONES[clave]
        q = select(d.modelo).order_by(getattr(d.modelo, d.orden))
        if solo_activos:
            q = q.where(d.modelo.activo.is_(True))
        return self.s.scalars(q).all()

    def obtener_de(self, clave, id_):
        return self.s.get(DEFINICIONES[clave].modelo, id_)

    def por_unico(self, clave, valor):
        d = DEFINICIONES[clave]
        return self.s.scalar(select(d.modelo).where(getattr(d.modelo, d.unico) == valor))

    def anio_actual(self):
        return self.s.scalar(select(AnioLectivo).where(AnioLectivo.activo.is_(True))
                             .order_by(AnioLectivo.anio.desc()).limit(1))
