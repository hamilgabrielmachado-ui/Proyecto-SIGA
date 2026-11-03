from controllers.base_controller import ControladorBase
from services import asistencia_service as svc


class AsistenciaController(ControladorBase):
    def asignaciones(self): return self._run(svc.asignaciones_disponibles, vacio=[])
    def asignaciones_consulta(self): return self._run(svc.asignaciones_consultables, vacio=[])
    def cargar_lista(self, id_asig, fecha): return self._run(svc.cargar_lista, id_asig, fecha)
    def guardar(self, id_asig, fecha, regs): return self._run(svc.guardar, id_asig, fecha, regs)
    def consultar(self, desde=None, hasta=None, id_asignacion=None, estado=None):
        return self._run(svc.consultar, desde, hasta, id_asignacion, None, estado, vacio=[])
