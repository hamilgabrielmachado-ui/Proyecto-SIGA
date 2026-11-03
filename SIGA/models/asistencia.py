from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class Asistencia(Base):
    __tablename__ = "asistencia"
    __table_args__ = (UniqueConstraint("id_sesion", "id_estudiante", name="uq_asistencia_sesion_estudiante"),)
    id_asistencia = Column(Integer, primary_key=True)
    id_sesion = Column(Integer, ForeignKey("sesion_asistencia.id_sesion", ondelete="CASCADE"), nullable=False)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante"), nullable=False)
    estado = Column(String(20), nullable=False)
    observacion = Column(String(200))

    sesion = relationship("SesionAsistencia", back_populates="registros")
    estudiante = relationship("Estudiante")
    justificacion = relationship("Justificacion", back_populates="asistencia", uselist=False,
                                 cascade="all, delete-orphan")
