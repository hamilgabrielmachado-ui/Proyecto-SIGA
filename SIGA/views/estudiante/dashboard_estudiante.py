from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from views.componentes import TarjetaResumen, crear_tabla, llenar_tabla, mostrar_error


class DashboardEstudiante(QWidget):
    def __init__(self, ctl):
        super().__init__()
        self.ctl = ctl
        lay = QVBoxLayout(self)
        self.saludo = QLabel("")
        self.saludo.setObjectName("Saludo")
        lay.addWidget(self.saludo)
        self.grupo = QLabel("")
        self.grupo.setObjectName("Nota")
        lay.addWidget(self.grupo)
        grid = QGridLayout()
        self.t_pct = TarjetaResumen("Asistencia")
        self.t_pres = TarjetaResumen("Presentes")
        self.t_aus = TarjetaResumen("Ausencias")
        self.t_tar = TarjetaResumen("Tardanzas")
        self.t_pend = TarjetaResumen("Justificaciones pendientes")
        for i, t in enumerate((self.t_pct, self.t_pres, self.t_aus, self.t_tar, self.t_pend)):
            grid.addWidget(t, 0, i)
        lay.addLayout(grid)
        sub = QLabel("Mi horario de hoy")
        sub.setObjectName("Subtitulo")
        lay.addWidget(sub)
        self.tabla = crear_tabla()
        lay.addWidget(self.tabla, 1)
        self.vacio = QLabel("No tiene clases programadas para hoy.")
        self.vacio.setObjectName("MensajeVacio")
        lay.addWidget(self.vacio)

    def refrescar(self):
        res = self.ctl.dashboard("estudiante")
        if not res.ok:
            mostrar_error(self, "No se pudo cargar el panel", res.mensaje)
            return
        d = res.datos
        a = d["asistencia"]
        self.saludo.setText(f"Hola, {d['nombre']}")
        self.grupo.setText(f"Grado y sección: {d['grupo']}" if d["grupo"] else "Aún no tiene una matrícula activa.")
        self.t_pct.actualizar("Sin datos" if a["porcentaje"] is None else f"{a['porcentaje']}%", f"{a['total']} registros")
        self.t_pres.actualizar(a["presente"])
        self.t_aus.actualizar(a["ausente"])
        self.t_tar.actualizar(a["tardanza"])
        self.t_pend.actualizar(d["pendientes"])
        filas = d["clases_hoy"]
        llenar_tabla(self.tabla, ["Horario", "Periodo", "Asignatura", "Docente"],
                     [[f["horario"], f["periodo"], f["asignatura"], f["profesor"]] for f in filas])
        self.tabla.setVisible(bool(filas))
        self.vacio.setVisible(not filas)
