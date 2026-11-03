from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base
from models.usuario_rol import usuario_rol


class Usuario(Base):
    __tablename__ = "usuario"
    id_usuario = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    debe_cambiar_password = Column(Boolean, nullable=False, default=False)
    intentos_fallidos = Column(Integer, nullable=False, default=0)
    bloqueado_hasta = Column(DateTime)
    ultimo_acceso = Column(DateTime)
    creado_en = Column(DateTime, nullable=False, default=datetime.now)
    id_profesor = Column(Integer, ForeignKey("profesor.id_profesor"), unique=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante"), unique=True)

    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")
    profesor = relationship("Profesor")
    estudiante = relationship("Estudiante")
