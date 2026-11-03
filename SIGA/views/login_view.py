from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from controllers.login_controller import LoginController
from views.componentes import boton


class LoginView(QWidget):
    acceso_concedido = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIGA — Iniciar sesión")
        self.setObjectName("LoginFondo")
        self.resize(900, 600)
        self.ctl = LoginController()
        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        lado = QFrame()
        lado.setObjectName("LoginLado")
        ll = QVBoxLayout(lado)
        ll.setContentsMargins(40, 40, 40, 40)
        ll.addStretch()
        for txt, nombre in (("SIGA", "LoginMarca"), ("Sistema Integral de Gestión\nde Asistencia Escolar", "LoginLema")):
            l = QLabel(txt)
            l.setObjectName(nombre)
            ll.addWidget(l)
        ll.addStretch()
        raiz.addWidget(lado, 4)

        derecha = QVBoxLayout()
        derecha.addStretch()
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setMaximumWidth(380)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(32, 32, 32, 32)
        cl.setSpacing(10)
        t = QLabel("Bienvenido")
        t.setObjectName("LoginTitulo")
        cl.addWidget(t)
        s = QLabel("Ingrese sus credenciales para continuar")
        s.setObjectName("Nota")
        cl.addWidget(s)
        cl.addSpacing(8)
        cl.addWidget(QLabel("Usuario"))
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Su nombre de usuario")
        cl.addWidget(self.usuario)
        cl.addWidget(QLabel("Contraseña"))
        self.clave = QLineEdit()
        self.clave.setEchoMode(QLineEdit.Password)
        self.clave.setPlaceholderText("Su contraseña")
        cl.addWidget(self.clave)
        self.error = QLabel("")
        self.error.setObjectName("MensajeError")
        self.error.setWordWrap(True)
        self.error.hide()
        cl.addWidget(self.error)
        self.btn = boton("Ingresar", "primario")
        self.btn.setDefault(True)
        self.btn.clicked.connect(self.ingresar)
        cl.addWidget(self.btn)
        fila = QHBoxLayout()
        fila.addStretch()
        fila.addWidget(card)
        fila.addStretch()
        derecha.addLayout(fila)
        derecha.addStretch()
        raiz.addLayout(derecha, 5)
        self.usuario.returnPressed.connect(self.clave.setFocus)
        self.clave.returnPressed.connect(self.ingresar)

    def ingresar(self):
        res = self.ctl.iniciar_sesion(self.usuario.text(), self.clave.text())
        if not res.ok:
            self.error.setText(res.mensaje)
            self.error.show()
            self.clave.clear()
            self.clave.setFocus()
            return
        self.error.hide()
        self.acceso_concedido.emit(res.datos)

    def limpiar(self):
        self.clave.clear()
        self.error.hide()
