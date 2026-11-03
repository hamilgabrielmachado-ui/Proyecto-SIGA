from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base
from models.rol_permiso import rol_permiso


class Permiso(Base):
    __tablename__ = "permiso"
    id_permiso = Column(Integer, primary_key=True)
    codigo = Column(String(60), unique=True, nullable=False)
    descripcion = Column(String(200))
    roles = relationship("Rol", secondary=rol_permiso, back_populates="permisos")
