from sqlalchemy import Boolean, Column, Integer, String

from database.base import Base


class CentroEducativo(Base):
    __tablename__ = "centro_educativo"
    id_centro = Column(Integer, primary_key=True)
    nombre = Column(String(150), unique=True, nullable=False)
    codigo = Column(String(30), unique=True)
    direccion = Column(String(200))
    activo = Column(Boolean, nullable=False, default=True)
