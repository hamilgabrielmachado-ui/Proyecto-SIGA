"""Punto de entrada de SIGA. La lógica vive en controllers/aplicacion_controller.py."""
import sys

from PySide6.QtWidgets import QApplication

from controllers.aplicacion_controller import AplicacionController


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SIGA")
    controlador = AplicacionController(app)
    sys.exit(controlador.iniciar())


if __name__ == "__main__":
    main()
