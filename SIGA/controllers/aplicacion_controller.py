"""Ciclo de vida de la aplicación: conexión, login, ventana principal y cierre de sesión."""
import logging

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from config import settings
from controllers.base_controller import ejecutar
from database.connection import probar_conexion
from database.init_db import inicializar
from views.componentes import mostrar_error, mostrar_info


def cargar_estilos(app, *nombres):
    css = ""
    for n in nombres:
        ruta = settings.STYLES_DIR / n
        if ruta.exists():
            css += ruta.read_text(encoding="utf-8") + "\n"
    app.setStyleSheet(css)


class AplicacionController(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app, self.login, self.ventana = app, None, None

    def iniciar(self) -> int:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
        ini = ejecutar(probar_conexion)
        if ini.ok:
            ini = ejecutar(inicializar)
        if not ini.ok:
            mostrar_error(None, "Error de conexión",
                          "No se pudo conectar con la base de datos.\n\nVerifique que MySQL esté activo y que los "
                          "datos del archivo .env (usuario, contraseña y nombre de la base) sean correctos.")
            return 1
        nuevo = ini.datos
        if nuevo:
            mostrar_info(None, "Administrador inicial creado",
                         f"Se creó el usuario administrador.\n\nUsuario: {nuevo[0]}\nContraseña temporal: {nuevo[1]}\n\n"
                         "Anótela ahora: no se volverá a mostrar. Se le pedirá cambiarla al ingresar.")
        self.mostrar_login()
        return self.app.exec()

    def mostrar_login(self):
        from views.login_view import LoginView
        cargar_estilos(self.app, "main.qss", "login.qss")
        self.login = LoginView()
        self.login.acceso_concedido.connect(self.abrir_principal)
        self.login.show()

    def abrir_principal(self, actor):
        from views.main_window import MainWindow
        from views.compartido.perfil_page import CambiarPasswordDialog
        cargar_estilos(self.app, "main.qss", {"Administrador": "admin.qss", "Docente": "docente.qss",
                                              "Estudiante": "estudiante.qss"}[actor.rol_principal])
        if actor.debe_cambiar_password:
            if not CambiarPasswordDialog(actor, obligatorio=True, parent=self.login).exec():
                self.login.limpiar()
                cargar_estilos(self.app, "main.qss", "login.qss")
                return
        self.login.close()
        self.ventana = MainWindow(actor)
        self.ventana.sesion_cerrada.connect(self.cerrar_sesion)
        self.ventana.showMaximized()

    def cerrar_sesion(self):
        if self.ventana:
            self.ventana.deleteLater()
            self.ventana = None
        self.mostrar_login()
