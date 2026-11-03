from sqlalchemy import or_, select

from models import Asistencia, Estudiante, Matricula, Usuario
from repositories.base_repository import BaseRepository


class EstudianteRepository(BaseRepository):
    modelo = Estudiante

    def buscar(self, texto="", activo=None):
        q = select(Estudiante).order_by(Estudiante.apellidos, Estudiante.nombres)
        if texto:
            p = f"%{texto}%"
            q = q.where(or_(Estudiante.nombres.ilike(p), Estudiante.apellidos.ilike(p),
                            Estudiante.codigo.ilike(p), Estudiante.cedula.ilike(p)))
        if activo is not None:
            q = q.where(Estudiante.activo.is_(activo))
        return self.s.scalars(q).all()

    def por_codigo(self, codigo):
        return self.s.scalar(select(Estudiante).where(Estudiante.codigo == codigo))

    def por_cedula(self, cedula):
        return self.s.scalar(select(Estudiante).where(Estudiante.cedula == cedula))

    def por_correo(self, correo):
        return self.s.scalar(select(Estudiante).where(Estudiante.correo == correo))

    def tiene_dependencias(self, id_estudiante) -> bool:
        for modelo in (Matricula, Asistencia, Usuario):
            if self.s.scalar(select(modelo).where(modelo.id_estudiante == id_estudiante).limit(1)):
                return True
        return False
