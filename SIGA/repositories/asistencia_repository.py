from sqlalchemy import or_, select

from models import (AnioLectivo, AsignacionDocente, Asignatura, Asistencia, Estudiante, Grado,
                    Justificacion, PeriodoClase, Profesor, Seccion, SesionAsistencia)
from repositories.base_repository import BaseRepository


class AsistenciaRepository(BaseRepository):
    modelo = Asistencia

    def sesion(self, id_asignacion, fecha):
        return self.s.scalar(select(SesionAsistencia).where(
            SesionAsistencia.id_asignacion == id_asignacion, SesionAsistencia.fecha == fecha))

    def registros_de_sesion(self, id_sesion):
        return {r.id_estudiante: r for r in self.s.scalars(
            select(Asistencia).where(Asistencia.id_sesion == id_sesion))}

    def consulta(self, desde=None, hasta=None, id_asignaciones=None, id_estudiante=None,
                 id_profesor=None, id_grado=None, id_seccion=None, id_anio=None, id_periodo=None,
                 id_asistencia=None, estados=None, id_justificacion=None, solo_justificadas=False,
                 estado_just=None):
        """Consulta amplia de asistencia con sus datos relacionados (una fila por registro)."""
        q = (select(Asistencia.id_asistencia, Asistencia.estado, Asistencia.observacion,
                    SesionAsistencia.fecha, AsignacionDocente.id_asignacion,
                    AsignacionDocente.id_profesor, AsignacionDocente.id_grado,
                    AsignacionDocente.id_seccion, AsignacionDocente.id_anio, AsignacionDocente.id_periodo,
                    Estudiante.id_estudiante, Estudiante.codigo, Estudiante.nombres, Estudiante.apellidos,
                    Grado.nombre.label("grado"), Seccion.nombre.label("seccion"),
                    Asignatura.nombre.label("asignatura"), PeriodoClase.nombre.label("periodo"),
                    AnioLectivo.anio, Profesor.nombres.label("prof_nombres"),
                    Profesor.apellidos.label("prof_apellidos"),
                    Justificacion.id_justificacion, Justificacion.estado.label("just_estado"),
                    Justificacion.motivo, Justificacion.comentario_revision)
             .join(SesionAsistencia, SesionAsistencia.id_sesion == Asistencia.id_sesion)
             .join(AsignacionDocente, AsignacionDocente.id_asignacion == SesionAsistencia.id_asignacion)
             .join(Estudiante, Estudiante.id_estudiante == Asistencia.id_estudiante)
             .join(Grado, Grado.id_grado == AsignacionDocente.id_grado)
             .join(Seccion, Seccion.id_seccion == AsignacionDocente.id_seccion)
             .join(Asignatura, Asignatura.id_asignatura == AsignacionDocente.id_asignatura)
             .join(PeriodoClase, PeriodoClase.id_periodo == AsignacionDocente.id_periodo)
             .join(AnioLectivo, AnioLectivo.id_anio == AsignacionDocente.id_anio)
             .join(Profesor, Profesor.id_profesor == AsignacionDocente.id_profesor)
             .outerjoin(Justificacion, Justificacion.id_asistencia == Asistencia.id_asistencia)
             .order_by(SesionAsistencia.fecha.desc(), PeriodoClase.hora_inicio, Estudiante.apellidos))
        if desde:
            q = q.where(SesionAsistencia.fecha >= desde)
        if hasta:
            q = q.where(SesionAsistencia.fecha <= hasta)
        if id_asignaciones is not None:
            q = q.where(AsignacionDocente.id_asignacion.in_(list(id_asignaciones)))
        filtros = [(Estudiante.id_estudiante, id_estudiante), (AsignacionDocente.id_profesor, id_profesor),
                   (AsignacionDocente.id_grado, id_grado), (AsignacionDocente.id_seccion, id_seccion),
                   (AsignacionDocente.id_anio, id_anio), (AsignacionDocente.id_periodo, id_periodo),
                   (Asistencia.id_asistencia, id_asistencia), (Justificacion.id_justificacion, id_justificacion)]
        for col, val in filtros:
            if val:
                q = q.where(col == val)
        if estados:
            q = q.where(Asistencia.estado.in_(list(estados)))
        if solo_justificadas:
            q = q.where(Justificacion.id_justificacion.is_not(None))
        if estado_just:
            q = q.where(Justificacion.estado == estado_just)
        return [dict(r._mapping) for r in self.s.execute(q)]
