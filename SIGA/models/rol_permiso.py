from sqlalchemy import Column, ForeignKey, Integer, Table

from database.base import Base

rol_permiso = Table(
    "rol_permiso", Base.metadata,
    Column("id_rol", Integer, ForeignKey("rol.id_rol", ondelete="CASCADE"), primary_key=True),
    Column("id_permiso", Integer, ForeignKey("permiso.id_permiso", ondelete="CASCADE"), primary_key=True),
)
