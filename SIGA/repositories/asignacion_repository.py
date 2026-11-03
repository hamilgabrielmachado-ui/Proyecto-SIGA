from sqlalchemy import or_, select

from models import (AnioLectivo, AsignacionDocente, Asignatura, CentroEducativo, Grado,
                    Modalidad, PeriodoClase, Profesor, Seccion)
from repositories.base_repository import BaseRepository


def _consulta_base():
    return (select(AsignacionDocente.id_asignacion.label("id"), AsignacionDocente.id_profesor,
                   AsignacionDocente.id_centro, AsignacionDocente.id_anio, AsignacionDocente.id_grado,
                   AsignacionDocente.id_seccion, AsignacionDocente.id_asignatura,
                   AsignacionDocente.id_periodo, AsignacionDocente.id_modalidad,
                   AsignacionDocente.dia_semana, Profesor.nombres.label("prof_nombres"),
                   Profesor.apellidos.label("prof_apellidos"), CentroEducativo.nombre.label("centro"),
                   AnioLectivo.anio, Grado.nombre.label("grado"), Seccion.nombre.label("seccion"),
                   Asignatura.nombre.label("asignatura"), PeriodoClase.nombre.label("periodo"),
                   PeriodoClase.hora_inicio, PeriodoClase.hora_fin, Modalidad.nombre.label("modalidad"))
            .join(Profesor, Profesor.id_profesor == AsignacionDocente.id_profesor)
            .join(CentroEducativo, CentroEducativo.id_centro == AsignacionDocente.id_centro)
            .join(AnioLectivo, AnioLectivo.id_anio == AsignacionDocente.id_anio)
            .join(Grado, Grado.id_grado == AsignacionDocente.id_grado)
            .join(Seccion, Seccion.id_seccion == AsignacionDocente.id_seccion)
            .join(Asignatura, Asignatura.id_asignatura == AsignacionDocente.id_asignatura)
            .join(PeriodoClase, PeriodoClase.id_periodo == AsignacionDocente.id_periodo)
            .join(Modalidad, Modalidad.id_modalidad == AsignacionDocente.id_modalidad)
            .order_by(AnioLectivo.anio.desc(), AsignacionDocente.dia_semana, PeriodoClase.hora_inicio))


class AsignacionRepository(BaseRepository):
    modelo = AsignacionDocente

    def listar(self, id_profesor=None, buscar="", id_anio=None, dia=None, grupo=None):
        q = _consulta_base()
        if id_profesor:
            q = q.where(AsignacionDocente.id_profesor == id_profesor)
        if id_anio:
            q = q.where(AsignacionDocente.id_anio == id_anio)
        if dia:
            q = q.where(AsignacionDocente.dia_semana == dia)
        if grupo:  # (id_anio, id_centro, id_grado, id_seccion)
            q = q.where(AsignacionDocente.id_anio == grupo[0], AsignacionDocente.id_centro == grupo[1],
                        AsignacionDocente.id_grado == grupo[2], AsignacionDocente.id_seccion == grupo[3])
        if buscar:
            p = f"%{buscar}%"
            q = q.where(or_(Profesor.nombres.ilike(p), Profesor.apellidos.ilike(p),
                            Asignatura.nombre.ilike(p), Grado.nombre.ilike(p)))
        return [dict(r._mapping) for r in self.s.execute(q)]

    def conflicto_profesor(self, d, excluir=None):
        q = select(AsignacionDocente).where(
            AsignacionDocente.id_profesor == d["id_profesor"], AsignacionDocente.id_anio == d["id_anio"],
            AsignacionDocente.id_periodo == d["id_periodo"], AsignacionDocente.dia_semana == d["dia_semana"])
        if excluir:
            q = q.where(AsignacionDocente.id_asignacion != excluir)
        return self.s.scalar(q) is not None

    def conflicto_grupo(self, d, excluir=None):
        q = select(AsignacionDocente).where(
            AsignacionDocente.id_anio == d["id_anio"], AsignacionDocente.id_centro == d["id_centro"],
            AsignacionDocente.id_grado == d["id_grado"], AsignacionDocente.id_seccion == d["id_seccion"],
            AsignacionDocente.id_periodo == d["id_periodo"], AsignacionDocente.dia_semana == d["dia_semana"])
        if excluir:
            q = q.where(AsignacionDocente.id_asignacion != excluir)
        return self.s.scalar(q) is not None
