from controllers.base_controller import ControladorBase
from services import estudiante_service as svc


class EstudianteController(ControladorBase):
    def listar(self, buscar="", activo=None): return self._run(svc.listar, buscar, activo, vacio=[])
    def crear(self, d): return self._run(svc.crear, d, ok="Estudiante registrado correctamente.")
    def actualizar(self, id_, d): return self._run(svc.actualizar, id_, d, ok="Estudiante actualizado correctamente.")
    def eliminar(self, id_): return self._run(svc.eliminar, id_, ok="Estudiante eliminado.")
    def opciones(self): return self._run(svc.opciones, vacio=[])
