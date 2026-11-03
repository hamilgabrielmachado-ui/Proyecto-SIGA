from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class AsignacionDocente(Base):
    __tablename__ = "asignacion_docente"
    __table_args__ = (
        UniqueConstraint("id_profesor", "id_anio", "id_periodo", "dia_semana", name="uq_asig_profesor_horario"),
        UniqueConstraint("id_anio", "id_centro", "id_grado", "id_seccion", "id_periodo", "dia_semana",
                         name="uq_asig_grupo_horario"),
    )
    id_asignacion = Column(Integer, primary_key=True)
    id_profesor = Column(Integer, ForeignKey("profesor.id_profesor"), nullable=False)
    id_centro = Column(Integer, ForeignKey("centro_educativo.id_centro"), nullable=False)
    id_anio = Column(Integer, ForeignKey("anio_lectivo.id_anio"), nullable=False)
    id_grado = Column(Integer, ForeignKey("grado.id_grado"), nullable=False)
    id_seccion = Column(Integer, ForeignKey("seccion.id_seccion"), nullable=False)
    id_asignatura = Column(Integer, ForeignKey("asignatura.id_asignatura"), nullable=False)
    id_periodo = Column(Integer, ForeignKey("periodo_clase.id_periodo"), nullable=False)
    id_modalidad = Column(Integer, ForeignKey("modalidad.id_modalidad"), nullable=False)
    dia_semana = Column(Integer, nullable=False)  # 1=Lunes ... 7=Domingo

    profesor = relationship("Profesor")
