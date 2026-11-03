"""Perfil, dashboards, auditoría y respaldos."""
from controllers.base_controller import ControladorBase
from services import auditoria_service, autenticacion_service, dashboard_service, respaldo_service


class SistemaController(ControladorBase):
    def perfil(self): return self._run(autenticacion_service.perfil, vacio={})
    def cambiar_password(self, actual, nueva, confirmar):
        return self._run(autenticacion_service.cambiar_password, actual, nueva, confirmar,
                         ok="Contraseña actualizada correctamente.")
    def dashboard(self, rol):
        return self._run(getattr(dashboard_service, rol), vacio={})
    def auditoria(self, texto="", desde=None, hasta=None):
        return self._run(auditoria_service.listar, texto, desde, hasta, vacio=[])
    def respaldo(self): return self._run(respaldo_service.crear_respaldo)
