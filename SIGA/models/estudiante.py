from sqlalchemy import Boolean, Column, Date, Integer, String

from database.base import Base


class Estudiante(Base):
    __tablename__ = "estudiante"
    id_estudiante = Column(Integer, primary_key=True)
    codigo = Column(String(30), unique=True, nullable=False)
    cedula = Column(String(20), unique=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date)
    sexo = Column(String(1), nullable=False)
    telefono = Column(String(20))
    correo = Column(String(120))
    activo = Column(Boolean, nullable=False, default=True)

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
