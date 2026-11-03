from controllers.base_controller import ControladorBase
from services import usuario_service as svc


class UsuarioController(ControladorBase):
    def listar(self, buscar=""): return self._run(svc.listar, buscar, vacio=[])
    def crear(self, d): return self._run(svc.crear, d, ok="Usuario creado. Deberá cambiar su contraseña al ingresar.")
    def estado(self, id_, activo): return self._run(svc.cambiar_estado, id_, activo, ok="Estado actualizado.")
    def restablecer(self, id_): return self._run(svc.restablecer_password, id_)
    def asignar_rol(self, id_, rol): return self._run(svc.asignar_rol, id_, rol, ok="Rol actualizado.")
    def profesores_libres(self): return self._run(svc.profesores_sin_usuario, vacio=[])
    def estudiantes_libres(self): return self._run(svc.estudiantes_sin_usuario, vacio=[])
