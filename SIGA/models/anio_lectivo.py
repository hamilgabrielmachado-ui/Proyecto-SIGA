from sqlalchemy import Boolean, Column, Integer, String

from database.base import Base


class AnioLectivo(Base):
    __tablename__ = "anio_lectivo"
    id_anio = Column(Integer, primary_key=True)
    anio = Column(Integer, unique=True, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
