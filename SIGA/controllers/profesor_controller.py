from controllers.base_controller import ControladorBase
from services import catalogo_service, profesor_service as svc


class ProfesorController(ControladorBase):
    def listar(self, buscar="", activo=None): return self._run(svc.listar, buscar, activo, vacio=[])
    def crear(self, d): return self._run(svc.crear, d, ok="Profesor registrado correctamente.")
    def actualizar(self, id_, d): return self._run(svc.actualizar, id_, d, ok="Profesor actualizado correctamente.")
    def eliminar(self, id_): return self._run(svc.eliminar, id_, ok="Profesor eliminado.")
    def opciones(self): return self._run(svc.opciones, vacio=[])
    def catalogo(self, clave): return self._run(catalogo_service.opciones, clave, vacio=[])
