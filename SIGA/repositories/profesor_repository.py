from sqlalchemy import or_, select

from models import AsignacionDocente, Profesor, Usuario
from repositories.base_repository import BaseRepository


class ProfesorRepository(BaseRepository):
    modelo = Profesor

    def buscar(self, texto="", activo=None):
        q = select(Profesor).order_by(Profesor.apellidos, Profesor.nombres)
        if texto:
            p = f"%{texto}%"
            q = q.where(or_(Profesor.nombres.ilike(p), Profesor.apellidos.ilike(p),
                            Profesor.cedula.ilike(p), Profesor.codigo_mined.ilike(p)))
        if activo is not None:
            q = q.where(Profesor.activo.is_(activo))
        return self.s.scalars(q).all()

    def por_cedula(self, cedula):
        return self.s.scalar(select(Profesor).where(Profesor.cedula == cedula))

    def por_mined(self, codigo):
        return self.s.scalar(select(Profesor).where(Profesor.codigo_mined == codigo))

    def tiene_dependencias(self, id_profesor) -> bool:
        for modelo in (AsignacionDocente, Usuario):
            if self.s.scalar(select(modelo).where(modelo.id_profesor == id_profesor).limit(1)):
                return True
        return False
