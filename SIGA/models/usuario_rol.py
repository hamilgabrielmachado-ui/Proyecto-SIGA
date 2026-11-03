from sqlalchemy import Column, ForeignKey, Integer, Table

from database.base import Base

usuario_rol = Table(
    "usuario_rol", Base.metadata,
    Column("id_usuario", Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True),
    Column("id_rol", Integer, ForeignKey("rol.id_rol"), primary_key=True),
)
