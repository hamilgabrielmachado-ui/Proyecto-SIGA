from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class Justificacion(Base):
    __tablename__ = "justificacion"
    id_justificacion = Column(Integer, primary_key=True)
    id_asistencia = Column(Integer, ForeignKey("asistencia.id_asistencia", ondelete="CASCADE"),
                           unique=True, nullable=False)
    motivo = Column(String(500), nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    fecha_solicitud = Column(DateTime, nullable=False, default=datetime.now)
    id_solicitante = Column(Integer, ForeignKey("usuario.id_usuario"))
    id_revisor = Column(Integer, ForeignKey("usuario.id_usuario"))
    fecha_revision = Column(DateTime)
    comentario_revision = Column(String(300))

    asistencia = relationship("Asistencia", back_populates="justificacion")
