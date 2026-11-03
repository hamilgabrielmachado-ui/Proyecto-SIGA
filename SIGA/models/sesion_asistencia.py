from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class SesionAsistencia(Base):
    __tablename__ = "sesion_asistencia"
    __table_args__ = (UniqueConstraint("id_asignacion", "fecha", name="uq_sesion_asignacion_fecha"),)
    id_sesion = Column(Integer, primary_key=True)
    id_asignacion = Column(Integer, ForeignKey("asignacion_docente.id_asignacion"), nullable=False)
    fecha = Column(Date, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    creado_en = Column(DateTime, nullable=False, default=datetime.now)

    asignacion = relationship("AsignacionDocente")
    registros = relationship("Asistencia", back_populates="sesion", cascade="all, delete-orphan")
