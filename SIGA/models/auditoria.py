from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from database.base import Base


class Auditoria(Base):
    __tablename__ = "auditoria"
    id_auditoria = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    username = Column(String(50))
    accion = Column(String(50), nullable=False)
    entidad = Column(String(50))
    id_entidad = Column(Integer)
    detalle = Column(Text)
    fecha = Column(DateTime, nullable=False, default=datetime.now)
