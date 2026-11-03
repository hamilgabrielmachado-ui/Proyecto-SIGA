from controllers.base_controller import ControladorBase
from services import justificacion_service as svc


class JustificacionController(ControladorBase):
    def listar(self, estado=None): return self._run(svc.listar, estado, vacio=[])
    def sin_justificar(self): return self._run(svc.ausencias_sin_justificar, vacio=[])
    def registrar(self, id_asistencia, motivo):
        return self._run(svc.registrar, id_asistencia, motivo, ok="Justificación registrada.")
    def resolver(self, id_, aprobar, comentario=""):
        return self._run(svc.resolver, id_, aprobar, comentario,
                         ok="Justificación aprobada." if aprobar else "Justificación rechazada.")
