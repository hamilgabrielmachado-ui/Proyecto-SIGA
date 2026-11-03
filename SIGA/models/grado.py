from sqlalchemy import Boolean, Column, Integer, String

from database.base import Base


class Grado(Base):
    __tablename__ = "grado"
    id_grado = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    orden = Column(Integer, nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True)
