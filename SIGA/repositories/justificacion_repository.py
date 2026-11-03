from sqlalchemy import select

from models import Justificacion
from repositories.base_repository import BaseRepository


class JustificacionRepository(BaseRepository):
    modelo = Justificacion

    def por_asistencia(self, id_asistencia):
        return self.s.scalar(select(Justificacion).where(Justificacion.id_asistencia == id_asistencia))
