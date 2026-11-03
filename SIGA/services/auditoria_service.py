from datetime import datetime

from database.connection import get_session
from models import Auditoria
from repositories.auditoria_repository import AuditoriaRepository
from services.permisos_service import requerir


def registrar(session, actor, accion, entidad=None, id_entidad=None, detalle=None, username=None):
    """Registra un evento dentro de la sesión actual (misma transacción de la operación)."""
    session.add(Auditoria(
        id_usuario=getattr(actor, "id_usuario", None),
        username=getattr(actor, "username", None) or username,
        accion=accion, entidad=entidad, id_entidad=id_entidad, detalle=detalle, fecha=datetime.now()))


def listar(actor, texto="", desde=None, hasta=None, limite=500):
    requerir(actor, "auditoria.consultar")
    d = datetime.combine(desde, datetime.min.time()) if desde else None
    h = datetime.combine(hasta, datetime.max.time()) if hasta else None
    with get_session() as s:
        return [{"id": a.id_auditoria, "fecha": a.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                 "usuario": a.username or "—", "accion": a.accion, "entidad": a.entidad or "",
                 "id_entidad": a.id_entidad or "", "detalle": a.detalle or ""}
                for a in AuditoriaRepository(s).listar(texto, d, h, limite)]
