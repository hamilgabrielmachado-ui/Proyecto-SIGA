from controllers.base_controller import ControladorBase
from services import catalogo_service as svc


class CatalogoController(ControladorBase):
    def definiciones(self): return svc.definiciones()
    def listar(self, clave, buscar=""): return self._run(svc.listar, clave, buscar, vacio=[])
    def crear(self, clave, d): return self._run(svc.crear, clave, d, ok="Registro guardado correctamente.")
    def actualizar(self, clave, id_, d): return self._run(svc.actualizar, clave, id_, d, ok="Registro actualizado correctamente.")
    def eliminar(self, clave, id_): return self._run(svc.eliminar, clave, id_, ok="Registro eliminado.")
    def opciones(self, clave, solo_activos=True): return self._run(svc.opciones, clave, solo_activos, vacio=[])
    def anio_actual(self): return self._run(svc.anio_actual)
