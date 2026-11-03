from controllers.base_controller import ControladorBase
from services import matricula_service as svc


class MatriculaController(ControladorBase):
    def listar(self, buscar="", id_anio=None, id_grado=None, id_seccion=None):
        return self._run(svc.listar, buscar, id_anio, id_grado, id_seccion, vacio=[])
    def crear(self, d): return self._run(svc.crear, d, ok="Matrícula registrada correctamente.")
    def actualizar(self, id_, d): return self._run(svc.actualizar, id_, d, ok="Matrícula actualizada correctamente.")
    def eliminar(self, id_): return self._run(svc.eliminar, id_, ok="Matrícula eliminada.")
