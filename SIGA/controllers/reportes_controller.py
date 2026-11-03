from controllers.base_controller import ControladorBase
from services import reportes_service as svc


class ReportesController(ControladorBase):
    tipos = svc.TIPOS
    def opciones(self): return self._run(svc.opciones, vacio={})
    def generar(self, tipo, filtros): return self._run(svc.generar, tipo, filtros)
    def exportar(self, reporte, formato): return self._run(svc.exportar, reporte, formato)
