from sqlalchemy import func, select

from models import Estudiante, Profesor, Rol, Usuario
from repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    modelo = Usuario

    def por_username(self, username):
        return self.s.scalar(select(Usuario).where(func.lower(Usuario.username) == username.lower()))

    def listar(self, buscar=""):
        q = select(Usuario).order_by(Usuario.username)
        if buscar:
            q = q.where(Usuario.username.ilike(f"%{buscar}%"))
        return self.s.scalars(q).all()

    def rol_por_nombre(self, nombre):
        return self.s.scalar(select(Rol).where(Rol.nombre == nombre))

    def profesores_sin_usuario(self):
        usados = select(Usuario.id_profesor).where(Usuario.id_profesor.is_not(None))
        return self.s.scalars(select(Profesor).where(Profesor.activo.is_(True),
                              Profesor.id_profesor.not_in(usados)).order_by(Profesor.apellidos)).all()

    def estudiantes_sin_usuario(self):
        usados = select(Usuario.id_estudiante).where(Usuario.id_estudiante.is_not(None))
        return self.s.scalars(select(Estudiante).where(Estudiante.activo.is_(True),
                              Estudiante.id_estudiante.not_in(usados)).order_by(Estudiante.apellidos)).all()
