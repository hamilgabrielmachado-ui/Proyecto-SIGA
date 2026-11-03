from sqlalchemy import select

from models import CentroEducativo
from repositories.base_repository import BaseRepository


class CentroRepository(BaseRepository):
    modelo = CentroEducativo

    def activos(self):
        return self.s.scalars(select(CentroEducativo).where(CentroEducativo.activo.is_(True))
                              .order_by(CentroEducativo.nombre)).all()
