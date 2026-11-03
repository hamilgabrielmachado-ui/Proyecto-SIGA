from sqlalchemy import Boolean, Column, Integer, String

from database.base import Base


class Turno(Base):
    __tablename__ = "turno"
    id_turno = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
