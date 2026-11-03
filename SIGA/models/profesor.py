from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class Profesor(Base):
    __tablename__ = "profesor"
    id_profesor = Column(Integer, primary_key=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    codigo_mined = Column(String(30), unique=True, nullable=False)
    telefono = Column(String(20))
    especialidad = Column(String(100))
    nivel_academico = Column(String(50))
    anios_experiencia = Column(Integer, nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True)
    id_centro = Column(Integer, ForeignKey("centro_educativo.id_centro"))
    id_turno = Column(Integer, ForeignKey("turno.id_turno"))

    centro = relationship("CentroEducativo")
    turno = relationship("Turno")

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
