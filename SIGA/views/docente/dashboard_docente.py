from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from views.componentes import TarjetaResumen, boton, crear_tabla, llenar_tabla, mostrar_error


class DashboardDocente(QWidget):
    ir_a = Signal(str)

    def __init__(self, ctl):
        super().__init__()
        self.ctl = ctl
        lay = QVBoxLayout(self)
        self.saludo = QLabel("")
        self.saludo.setObjectName("Saludo")
        lay.addWidget(self.saludo)
        grid = QGridLayout()
        self.t_grupos = TarjetaResumen("Grupos / asignaturas")
        self.t_hoy = TarjetaResumen("Clases de hoy")
        self.t_asis = TarjetaResumen("Asistencia de mis grupos (30 días)")
        self.t_pend = TarjetaResumen("Justificaciones pendientes")
        for i, t in enumerate((self.t_grupos, self.t_hoy, self.t_asis, self.t_pend)):
            grid.addWidget(t, 0, i)
        lay.addLayout(grid)
        b = boton("Registrar asistencia", "primario")
        b.clicked.connect(lambda: self.ir_a.emit("asistencia"))
        lay.addWidget(b)
        sub = QLabel("Horario de hoy")
        sub.setObjectName("Subtitulo")
        lay.addWidget(sub)
        self.tabla = crear_tabla()
        lay.addWidget(self.tabla, 1)
        self.vacio = QLabel("No tiene clases programadas para hoy.")
        self.vacio.setObjectName("MensajeVacio")
        lay.addWidget(self.vacio)

    def refrescar(self):
        res = self.ctl.dashboard("docente")
        if not res.ok:
            mostrar_error(self, "No se pudo cargar el panel", res.mensaje)
            return
        d = res.datos
        self.saludo.setText(f"Bienvenido(a), {d['nombre']}")
        self.t_grupos.actualizar(d["grupos"])
        self.t_hoy.actualizar(len(d["clases_hoy"]))
        a = d["asistencia"]
        self.t_asis.actualizar("Sin datos" if a["porcentaje"] is None else f"{a['porcentaje']}%",
                               f"{a['ausente']} ausencias · {a['tardanza']} tardanzas")
        self.t_pend.actualizar(d["pendientes"])
        filas = d["clases_hoy"]
        llenar_tabla(self.tabla, ["Horario", "Periodo", "Asignatura", "Grupo"],
                     [[f["horario"], f["periodo"], f["asignatura"], f["grupo"]] for f in filas])
        self.tabla.setVisible(bool(filas))
        self.vacio.setVisible(not filas)
