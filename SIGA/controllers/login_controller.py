from controllers.base_controller import ejecutar
from services import autenticacion_service


class LoginController:
    def iniciar_sesion(self, username, password):
        return ejecutar(autenticacion_service.iniciar_sesion, username, password)
