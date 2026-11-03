from sqlalchemy import Boolean, Column, Integer, String

from database.base import Base


class Seccion(Base):
    __tablename__ = "seccion"
    id_seccion = Column(Integer, primary_key=True)
    nombre = Column(String(20), unique=True, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
