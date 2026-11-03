from sqlalchemy import and_, or_, select

from models import (AnioLectivo, AsignacionDocente, CentroEducativo, Estudiante, Grado,
                    Matricula, Seccion)
from repositories.base_repository import BaseRepository


class MatriculaRepository(BaseRepository):
    modelo = Matricula

    def listar(self, buscar="", id_anio=None, id_grado=None, id_seccion=None):
        q = (select(Matricula.id_matricula.label("id"), Matricula.estado, Matricula.fecha,
                    Matricula.id_estudiante, Matricula.id_anio, Matricula.id_centro,
                    Matricula.id_grado, Matricula.id_seccion,
                    Estudiante.codigo, Estudiante.nombres, Estudiante.apellidos,
                    AnioLectivo.anio, CentroEducativo.nombre.label("centro"),
                    Grado.nombre.label("grado"), Seccion.nombre.label("seccion"))
             .join(Estudiante, Estudiante.id_estudiante == Matricula.id_estudiante)
             .join(AnioLectivo, AnioLectivo.id_anio == Matricula.id_anio)
             .join(CentroEducativo, CentroEducativo.id_centro == Matricula.id_centro)
             .join(Grado, Grado.id_grado == Matricula.id_grado)
             .join(Seccion, Seccion.id_seccion == Matricula.id_seccion)
             .order_by(AnioLectivo.anio.desc(), Grado.orden, Seccion.nombre, Estudiante.apellidos))
        if buscar:
            p = f"%{buscar}%"
            q = q.where(or_(Estudiante.nombres.ilike(p), Estudiante.apellidos.ilike(p),
                            Estudiante.codigo.ilike(p)))
        for col, val in ((Matricula.id_anio, id_anio), (Matricula.id_grado, id_grado),
                         (Matricula.id_seccion, id_seccion)):
            if val:
                q = q.where(col == val)
        return [dict(r._mapping) for r in self.s.execute(q)]

    def existe(self, id_estudiante, id_anio, excluir=None):
        q = select(Matricula).where(Matricula.id_estudiante == id_estudiante, Matricula.id_anio == id_anio)
        if excluir:
            q = q.where(Matricula.id_matricula != excluir)
        return self.s.scalar(q) is not None

    def estudiantes_del_grupo(self, id_anio, id_centro, id_grado, id_seccion):
        q = (select(Estudiante).join(Matricula, Matricula.id_estudiante == Estudiante.id_estudiante)
             .where(Matricula.id_anio == id_anio, Matricula.id_centro == id_centro,
                    Matricula.id_grado == id_grado, Matricula.id_seccion == id_seccion,
                    Matricula.estado == "activa", Estudiante.activo.is_(True))
             .order_by(Estudiante.apellidos, Estudiante.nombres))
        return self.s.scalars(q).all()

    def matricula_activa(self, id_estudiante):
        """Matrícula activa más reciente del estudiante (año lectivo más alto)."""
        q = (select(Matricula).join(AnioLectivo, AnioLectivo.id_anio == Matricula.id_anio)
             .where(Matricula.id_estudiante == id_estudiante, Matricula.estado == "activa")
             .order_by(AnioLectivo.anio.desc()).limit(1))
        return self.s.scalar(q)

    def estudiantes_de_profesor(self, id_profesor):
        q = (select(Estudiante).distinct()
             .join(Matricula, Matricula.id_estudiante == Estudiante.id_estudiante)
             .join(AsignacionDocente, and_(AsignacionDocente.id_anio == Matricula.id_anio,
                                           AsignacionDocente.id_centro == Matricula.id_centro,
                                           AsignacionDocente.id_grado == Matricula.id_grado,
                                           AsignacionDocente.id_seccion == Matricula.id_seccion))
             .where(AsignacionDocente.id_profesor == id_profesor)
             .order_by(Estudiante.apellidos, Estudiante.nombres))
        return self.s.scalars(q).all()
