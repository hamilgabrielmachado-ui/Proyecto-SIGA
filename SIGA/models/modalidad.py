from sqlalchemy import Boolean, Column, Integer, String

from database.base import Base


class Modalidad(Base):
    __tablename__ = "modalidad"
    id_modalidad = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
