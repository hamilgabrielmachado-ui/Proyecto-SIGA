from PySide6.QtWidgets import QFormLayout, QFrame, QLabel, QVBoxLayout, QWidget

from controllers.base_controller import ejecutar
from services import autenticacion_service
from views.componentes import Campo, FormularioDialog, boton, mostrar_error, mostrar_info


class CambiarPasswordDialog(FormularioDialog):
    def __init__(self, actor, obligatorio=False, parent=None):
        def guardar(v):
            res = ejecutar(autenticacion_service.cambiar_password, actor, v["actual"], v["nueva"], v["confirmar"])
            return res.ok, res.mensaje
        super().__init__("Cambiar contraseña" if not obligatorio else "Debe cambiar su contraseña", [
            Campo("actual", "Contraseña actual", "password", True),
            Campo("nueva", "Nueva contraseña", "password", True, placeholder="Mínimo 8, letras y números"),
            Campo("confirmar", "Confirmar nueva contraseña", "password", True)], guardar, parent, "Cambiar")
        if obligatorio:
            self.error.setText("Por seguridad, debe establecer una contraseña nueva antes de continuar.")
            self.error.show()


class PerfilPage(QWidget):
    def __init__(self, ctl):
        super().__init__()
        self.ctl = ctl
        self.actor = ctl.actor
        lay = QVBoxLayout(self)
        card = QFrame()
        card.setObjectName("Tarjeta")
        card.setMaximumWidth(620)
        self.form = QFormLayout(card)
        self.form.setVerticalSpacing(10)
        lay.addWidget(card)
        b = boton("Cambiar contraseña", "primario")
        b.clicked.connect(self._cambiar)
        lay.addWidget(b)
        lay.addStretch()

    def refrescar(self):
        res = self.ctl.perfil()
        if not res.ok:
            mostrar_error(self, "No se pudo cargar el perfil", res.mensaje)
            return
        while self.form.rowCount():
            self.form.removeRow(0)
        for k, v in res.datos.items():
            etiqueta = QLabel(k)
            etiqueta.setObjectName("Nota")
            self.form.addRow(etiqueta, QLabel(str(v)))

    def _cambiar(self):
        if CambiarPasswordDialog(self.actor, parent=self).exec():
            mostrar_info(self, "Contraseña actualizada", "Su contraseña fue cambiada correctamente.")
