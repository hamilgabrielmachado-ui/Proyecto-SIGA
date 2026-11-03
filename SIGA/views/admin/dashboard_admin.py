from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from views.componentes import TarjetaResumen, boton, mostrar_error


class DashboardAdmin(QWidget):
    ir_a = Signal(str)

    def __init__(self, ctl):
        super().__init__()
        self.ctl = ctl
        lay = QVBoxLayout(self)
        self.saludo = QLabel("Panel de administración")
        self.saludo.setObjectName("Saludo")
        lay.addWidget(self.saludo)
        grid = QGridLayout()
        self.t_est = TarjetaResumen("Estudiantes activos")
        self.t_prof = TarjetaResumen("Profesores activos")
        self.t_mat = TarjetaResumen("Matrículas activas")
        self.t_asis = TarjetaResumen("Asistencia (últimos 30 días)")
        self.t_pend = TarjetaResumen("Justificaciones pendientes")
        for i, t in enumerate((self.t_est, self.t_prof, self.t_mat, self.t_asis, self.t_pend)):
            grid.addWidget(t, i // 3, i % 3)
        lay.addLayout(grid)
        titulo = QLabel("Accesos rápidos")
        titulo.setObjectName("Subtitulo")
        lay.addWidget(titulo)
        fila = QHBoxLayout()
        for clave, txt in (("estudiantes", "Estudiantes"), ("profesores", "Profesores"), ("matriculas", "Matrículas"),
                           ("asignaciones", "Asignaciones"), ("asistencia", "Registrar asistencia"),
                           ("reportes", "Reportes")):
            b = boton(txt, "secundario")
            b.clicked.connect(lambda _=False, k=clave: self.ir_a.emit(k))
            fila.addWidget(b)
        fila.addStretch()
        lay.addLayout(fila)
        lay.addStretch()

    def refrescar(self):
        res = self.ctl.dashboard("admin")
        if not res.ok:
            mostrar_error(self, "No se pudo cargar el panel", res.mensaje)
            return
        d = res.datos
        self.t_est.actualizar(d["estudiantes"])
        self.t_prof.actualizar(d["profesores"])
        self.t_mat.actualizar(d["matriculas"], f"Año lectivo {d['anio']}" if d["anio"] else "Sin año lectivo activo")
        a = d["asistencia"]
        self.t_asis.actualizar("Sin datos" if a["porcentaje"] is None else f"{a['porcentaje']}%",
                               f"{a['presente']} presentes · {a['ausente']} ausentes · {a['tardanza']} tardanzas")
        self.t_pend.actualizar(d["pendientes"])
