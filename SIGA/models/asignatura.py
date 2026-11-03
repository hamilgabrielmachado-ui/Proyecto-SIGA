from sqlalchemy import Boolean, Column, Integer, String

from database.base import Base


class Asignatura(Base):
    __tablename__ = "asignatura"
    id_asignatura = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(20))
    activo = Column(Boolean, nullable=False, default=True)
