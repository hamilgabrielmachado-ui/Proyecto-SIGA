from sqlalchemy import Boolean, Column, Integer, String, Time

from database.base import Base


class PeriodoClase(Base):
    __tablename__ = "periodo_clase"
    id_periodo = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
