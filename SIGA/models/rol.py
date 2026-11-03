from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base
from models.rol_permiso import rol_permiso
from models.usuario_rol import usuario_rol


class Rol(Base):
    __tablename__ = "rol"
    id_rol = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200))
    usuarios = relationship("Usuario", secondary=usuario_rol, back_populates="roles")
    permisos = relationship("Permiso", secondary=rol_permiso, back_populates="roles")
