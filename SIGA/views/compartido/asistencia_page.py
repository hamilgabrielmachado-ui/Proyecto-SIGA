from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (QComboBox, QDateEdit, QHBoxLayout, QLabel, QLineEdit, QTableWidgetItem, QVBoxLayout,
                               QWidget)

from utils.constantes import ESTADOS_ASISTENCIA
from views.componentes import (COLORES_ESTADO, PaginaCrud, boton, combo, confirmar, crear_tabla, mostrar_aviso,
                               mostrar_error, mostrar_info)


def _fecha(w):
    d = w.date()
    return date(d.year(), d.month(), d.day())


def _selector_fecha(dias_atras=0):
    w = QDateEdit(QDate.currentDate().addDays(-dias_atras))
    w.setCalendarPopup(True)
    w.setDisplayFormat("yyyy-MM-dd")
    return w


class AsistenciaRegistroPage(QWidget):
    """Pasar lista: elegir clase y fecha, marcar estado de cada estudiante y guardar."""

    def __init__(self, ctl):
        super().__init__()
        self.ctl = ctl
        lay = QVBoxLayout(self)
        fila = QHBoxLayout()
        fila.addWidget(QLabel("Clase"))
        self.clase = QComboBox()
        self.clase.setMinimumWidth(420)
        fila.addWidget(self.clase, 1)
        fila.addWidget(QLabel("Fecha"))
        self.fecha = _selector_fecha()
        self.fecha.setMaximumDate(QDate.currentDate())
        fila.addWidget(self.fecha)
        self.btn_cargar = boton("Cargar lista", "secundario")
        self.btn_cargar.clicked.connect(self.cargar_lista)
        fila.addWidget(self.btn_cargar)
        lay.addLayout(fila)
        self.info = QLabel("")
        self.info.setObjectName("Nota")
        lay.addWidget(self.info)
        self.tabla = crear_tabla()
        self.tabla.setSortingEnabled(False)
        self.tabla.verticalHeader().setDefaultSectionSize(46)
        lay.addWidget(self.tabla, 1)
        pie = QHBoxLayout()
        self.todos = boton("Marcar todos presentes")
        self.todos.clicked.connect(self._todos_presentes)
        pie.addWidget(self.todos)
        self.resumen = QLabel("")
        pie.addWidget(self.resumen)
        pie.addStretch()
        self.btn_guardar = boton("Guardar asistencia", "primario")
        self.btn_guardar.clicked.connect(self.guardar)
        pie.addWidget(self.btn_guardar)
        lay.addLayout(pie)
        self.estado_msg = QLabel("")
        self.estado_msg.setObjectName("MensajeExito")
        lay.addWidget(self.estado_msg)
        self._estudiantes, self._combos = [], []
        self._set_activo(False)

    def _set_activo(self, v):
        self.btn_guardar.setEnabled(v)
        self.todos.setEnabled(v)

    def refrescar(self):
        res = self.ctl.asignaciones()
        if not res.ok:
            mostrar_error(self, "No se pudieron cargar sus clases", res.mensaje)
        self._asig = res.datos or []
        actual = self.clase.currentData()
        self.clase.clear()
        for a in self._asig:
            self.clase.addItem(a["texto"], a["id"])
        if actual is not None and self.clase.findData(actual) >= 0:
            self.clase.setCurrentIndex(self.clase.findData(actual))
        self.btn_cargar.setEnabled(bool(self._asig))
        self.info.setText("" if self._asig else "No tiene clases asignadas. Solicite al administrador que registre sus asignaciones.")

    def cargar_lista(self):
        id_asig = self.clase.currentData()
        if id_asig is None:
            return
        res = self.ctl.cargar_lista(id_asig, _fecha(self.fecha))
        if not res.ok:
            mostrar_aviso(self, "No se pudo cargar la lista", res.mensaje)
            return
        self._estudiantes = res.datos["estudiantes"]
        self.tabla.clear()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Código", "Estudiante", "Estado", "Observación"])
        self.tabla.setRowCount(len(self._estudiantes))
        self._combos, self._obs = [], []
        for i, e in enumerate(self._estudiantes):
            self.tabla.setItem(i, 0, QTableWidgetItem(e["codigo"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(e["nombre"]))
            c = QComboBox()
            for est in ESTADOS_ASISTENCIA:
                c.addItem(est.capitalize(), est)
            c.setCurrentIndex(c.findData(e["estado"]))
            c.currentIndexChanged.connect(self._actualizar_resumen)
            self.tabla.setRowHeight(i, 46)
            self.tabla.setCellWidget(i, 2, c)
            o = QLineEdit(e["observacion"])
            o.setMaxLength(200)
            self.tabla.setCellWidget(i, 3, o)
            self._combos.append(c)
            self._obs.append(o)
        existe = res.datos["existe"]
        self.info.setText("Ya existe asistencia para esta clase y fecha: puede revisarla y modificarla."
                          if existe else "Sesión nueva. Todos los estudiantes inician como «Presente».")
        if not self._estudiantes:
            self.info.setText("No hay estudiantes matriculados (activos) en este grupo.")
        self._set_activo(bool(self._estudiantes))
        self._actualizar_resumen()

    def _todos_presentes(self):
        for c in self._combos:
            c.setCurrentIndex(c.findData("presente"))

    def _actualizar_resumen(self):
        n = {e: sum(1 for c in self._combos if c.currentData() == e) for e in ESTADOS_ASISTENCIA}
        self.resumen.setText(f"Presentes: {n['presente']}   Ausentes: {n['ausente']}   Tardanzas: {n['tardanza']}")

    def guardar(self):
        if not self._estudiantes:
            return
        if not confirmar(self, "¿Guardar la asistencia de esta clase?", "Guardar asistencia"):
            return
        regs = [{"id_estudiante": e["id_estudiante"], "estado": self._combos[i].currentData(),
                 "observacion": self._obs[i].text()} for i, e in enumerate(self._estudiantes)]
        res = self.ctl.guardar(self.clase.currentData(), _fecha(self.fecha), regs)
        if not res.ok:
            mostrar_aviso(self, "No se pudo guardar", res.mensaje)
            return
        d = res.datos
        mostrar_info(self, "Asistencia guardada",
                     f"{'Sesión registrada' if d['creada'] else 'Sesión actualizada'} correctamente.\n\n"
                     f"Presentes: {d['presentes']}\nAusentes: {d['ausentes']}\nTardanzas: {d['tardanzas']}")
        self.tabla.setRowCount(0)
        self._estudiantes = []
        self._set_activo(False)
        self.resumen.setText("")
        self.info.setText("Seleccione una clase y cargue la lista para continuar.")


class AsistenciaConsultaPage(PaginaCrud):
    puede_crear = puede_editar = puede_eliminar = False
    texto_busqueda = "Buscar por estudiante o asignatura…"
    mensaje_vacio = "No hay registros de asistencia para los filtros seleccionados."

    def __init__(self, ctl, parent=None):
        self._es_est = False
        super().__init__(ctl, parent)

    def filtros_extra(self):
        self.desde = _selector_fecha(30)
        self.hasta = _selector_fecha()
        self.f_estado = combo([(e, e.capitalize()) for e in ESTADOS_ASISTENCIA], "Todos los estados")
        self.f_clase = combo([], "Todas las clases")
        for w in (self.desde, self.hasta):
            w.dateChanged.connect(self.refrescar)
        self.f_estado.currentIndexChanged.connect(self.refrescar)
        self.f_clase.currentIndexChanged.connect(self.refrescar)
        return [QLabel("Desde"), self.desde, QLabel("Hasta"), self.hasta, self.f_estado, self.f_clase]

    def refrescar(self):
        if not getattr(self, "_clases_cargadas", False):
            res = self.ctl.asignaciones_consulta()
            self._es_est = self.ctl.actor.es_estudiante
            self.f_clase.blockSignals(True)
            for a in res.datos or []:
                self.f_clase.addItem(a["texto"], a["id"])
            self.f_clase.blockSignals(False)
            self.f_clase.setVisible(not self._es_est)
            self._clases_cargadas = True
        super().refrescar()

    @property
    def columnas(self):
        cols = [("fecha", "Fecha"), ("grupo", "Grupo"), ("asignatura", "Asignatura"), ("periodo", "Periodo"),
                ("estudiante", "Estudiante"), ("estado", "Estado"), ("justificacion", "Justificación"),
                ("observacion", "Observación")]
        return [c for c in cols if not (self._es_est and c[0] == "estudiante")]

    @columnas.setter
    def columnas(self, v): pass

    def cargar(self, texto):
        res = self.ctl.consultar(_fecha(self.desde), _fecha(self.hasta), self.f_clase.currentData(),
                                 self.f_estado.currentData())
        if res.ok and texto:
            t = texto.lower()
            res.datos = [f for f in res.datos if t in f"{f['estudiante']} {f['asignatura']}".lower()]
        return res
