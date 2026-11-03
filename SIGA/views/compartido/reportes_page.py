from datetime import date
import os
import sys

from PySide6.QtCore import QDate, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QComboBox, QDateEdit, QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from views.componentes import boton, combo, confirmar, crear_tabla, llenar_tabla, mostrar_aviso, mostrar_error, mostrar_info


def _f(w):
    d = w.date()
    return date(d.year(), d.month(), d.day())


class ReportesPage(QWidget):
    def __init__(self, ctl):
        super().__init__()
        self.ctl = ctl
        self.reporte = None
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.tipo = QComboBox()
        for clave, (nombre, _, _) in ctl.tipos.items():
            self.tipo.addItem(nombre, clave)
        self.tipo.currentIndexChanged.connect(self._ajustar)
        self.desde, self.hasta = QDateEdit(QDate.currentDate().addDays(-30)), QDateEdit(QDate.currentDate())
        for d in (self.desde, self.hasta):
            d.setCalendarPopup(True)
            d.setDisplayFormat("yyyy-MM-dd")
        fila_f = QHBoxLayout()
        fila_f.addWidget(self.desde)
        fila_f.addWidget(QLabel("a"))
        fila_f.addWidget(self.hasta)
        fila_f.addStretch()
        self.c = {k: combo([], "Seleccione…") for k in ("estudiante", "asignacion", "grado", "seccion", "profesor")}
        form.addRow("Tipo de reporte", self.tipo)
        form.addRow("Periodo", fila_f)
        self._filas = {}
        for k, txt in (("estudiante", "Estudiante"), ("asignacion", "Clase / grupo"), ("grado", "Grado"),
                       ("seccion", "Sección"), ("profesor", "Docente")):
            self._filas[k] = (QLabel(txt), self.c[k])
            form.addRow(*self._filas[k])
        lay.addLayout(form)
        acciones = QHBoxLayout()
        gen = boton("Generar vista previa", "primario")
        gen.clicked.connect(self.generar)
        self.b_pdf, self.b_xls = boton("Exportar PDF"), boton("Exportar Excel")
        self.b_pdf.clicked.connect(lambda: self.exportar("pdf"))
        self.b_xls.clicked.connect(lambda: self.exportar("xlsx"))
        for b in (gen, self.b_pdf, self.b_xls):
            acciones.addWidget(b)
        acciones.addStretch()
        lay.addLayout(acciones)
        self.resumen = QLabel("")
        self.resumen.setObjectName("Nota")
        lay.addWidget(self.resumen)
        self.tabla = crear_tabla()
        lay.addWidget(self.tabla, 1)
        self.b_pdf.setEnabled(False)
        self.b_xls.setEnabled(False)
        self._cargado = False

    def refrescar(self):
        if not self._cargado:
            res = self.ctl.opciones()
            if not res.ok:
                mostrar_error(self, "No se pudieron cargar los filtros", res.mensaje)
                return
            o = res.datos
            for k, clave in (("estudiante", "estudiantes"), ("asignacion", "asignaciones"), ("grado", "grados"),
                             ("seccion", "secciones"), ("profesor", "profesores")):
                for v, t in o.get(clave, []):
                    self.c[k].addItem(str(t), v)
            self._cargado = True
        self._ajustar()

    def _ajustar(self):
        req = self.ctl.tipos[self.tipo.currentData()][1]
        for k, (etq, w) in self._filas.items():
            etq.setVisible(k in req)
            w.setVisible(k in req)

    def generar(self):
        filtros = {k: w.currentData() for k, w in self.c.items()}
        filtros.update({"desde": _f(self.desde), "hasta": _f(self.hasta)})
        res = self.ctl.generar(self.tipo.currentData(), filtros)
        if not res.ok:
            mostrar_aviso(self, "No se pudo generar el reporte", res.mensaje)
            return
        self.reporte = res.datos
        llenar_tabla(self.tabla, self.reporte.columnas, self.reporte.filas)
        self.resumen.setText(f"{self.reporte.titulo} — {len(self.reporte.filas)} fila(s). {self.reporte.resumen}")
        ok = bool(self.reporte.filas)
        self.b_pdf.setEnabled(ok)
        self.b_xls.setEnabled(ok)
        if not ok:
            mostrar_info(self, "Sin resultados", "No hay datos para los filtros seleccionados.")

    def exportar(self, formato):
        if not self.reporte:
            return
        res = self.ctl.exportar(self.reporte, formato)
        if not res.ok:
            mostrar_aviso(self, "No se pudo exportar", res.mensaje)
            return
        if confirmar(self, f"Reporte guardado en:\n{res.datos}\n\n¿Desea abrirlo ahora?", "Reporte generado"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(res.datos)))
