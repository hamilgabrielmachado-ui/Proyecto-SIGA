from sqlalchemy import or_, select

from models import Auditoria
from repositories.base_repository import BaseRepository


class AuditoriaRepository(BaseRepository):
    modelo = Auditoria

    def listar(self, texto="", desde=None, hasta=None, limite=500):
        q = select(Auditoria).order_by(Auditoria.fecha.desc(), Auditoria.id_auditoria.desc()).limit(limite)
        if texto:
            p = f"%{texto}%"
            q = q.where(or_(Auditoria.username.ilike(p), Auditoria.accion.ilike(p),
                            Auditoria.entidad.ilike(p), Auditoria.detalle.ilike(p)))
        if desde:
            q = q.where(Auditoria.fecha >= desde)
        if hasta:
            q = q.where(Auditoria.fecha <= hasta)
        return self.s.scalars(q).all()
