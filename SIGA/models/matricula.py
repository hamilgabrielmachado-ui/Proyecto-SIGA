from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class Matricula(Base):
    __tablename__ = "matricula"
    __table_args__ = (UniqueConstraint("id_estudiante", "id_anio", name="uq_matricula_estudiante_anio"),)
    id_matricula = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante"), nullable=False)
    id_anio = Column(Integer, ForeignKey("anio_lectivo.id_anio"), nullable=False)
    id_centro = Column(Integer, ForeignKey("centro_educativo.id_centro"), nullable=False)
    id_grado = Column(Integer, ForeignKey("grado.id_grado"), nullable=False)
    id_seccion = Column(Integer, ForeignKey("seccion.id_seccion"), nullable=False)
    estado = Column(String(20), nullable=False, default="activa")
    fecha = Column(Date, nullable=False, default=date.today)

    estudiante = relationship("Estudiante")
