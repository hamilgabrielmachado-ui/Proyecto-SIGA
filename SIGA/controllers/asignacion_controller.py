from controllers.base_controller import ControladorBase
from services import asignacion_service as svc


class AsignacionController(ControladorBase):
    def listar(self, buscar=""): return self._run(svc.listar, buscar, vacio=[])
    def crear(self, d): return self._run(svc.crear, d, ok="Asignación registrada correctamente.")
    def actualizar(self, id_, d): return self._run(svc.actualizar, id_, d, ok="Asignación actualizada correctamente.")
    def eliminar(self, id_): return self._run(svc.eliminar, id_, ok="Asignación eliminada.")
    def mi_horario(self, solo_hoy=False): return self._run(svc.mi_horario, solo_hoy, vacio=[])
