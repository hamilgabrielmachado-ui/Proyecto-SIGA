"""Componentes reutilizables: mensajes, formularios, tablas y tarjetas."""
from dataclasses import dataclass, field
from datetime import date, datetime, time

from PySide6.QtCore import QDate, QSignalBlocker, Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
                               QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
                               QPlainTextEdit, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

COLORES_ESTADO = {"presente": "#15803D", "aprobada": "#15803D", "activa": "#15803D",
                  "ausente": "#B91C1C", "rechazada": "#B91C1C", "tardanza": "#B45309",
                  "pendiente": "#B45309", "Sin justificar": "#B91C1C", "retirada": "#B45309"}


# ---------------- mensajes ----------------
def _caja(parent, icono, titulo, texto, botones=QMessageBox.Ok):
    m = QMessageBox(icono, titulo, texto, botones, parent)
    return m


def mostrar_info(parent, titulo, texto):
    _caja(parent, QMessageBox.Information, titulo, texto).exec()


def mostrar_error(parent, titulo, texto):
    _caja(parent, QMessageBox.Critical, titulo, texto).exec()


def mostrar_aviso(parent, titulo, texto):
    _caja(parent, QMessageBox.Warning, titulo, texto).exec()


def confirmar(parent, texto, titulo="Confirmar") -> bool:
    m = _caja(parent, QMessageBox.Question, titulo, texto, QMessageBox.Yes | QMessageBox.No)
    m.button(QMessageBox.Yes).setText("Sí")
    m.button(QMessageBox.No).setText("No")
    m.setDefaultButton(QMessageBox.No)
    return m.exec() == QMessageBox.Yes


def boton(texto, variante="secundario", parent=None):
    b = QPushButton(texto, parent)
    b.setProperty("variante", variante)
    b.setCursor(Qt.PointingHandCursor)
    return b


# ---------------- formularios ----------------
@dataclass
class Campo:
    nombre: str
    etiqueta: str
    tipo: str = "texto"   # texto, password, entero, fecha, fecha_req, hora, combo, check, multilinea
    requerido: bool = False
    opciones: list = field(default_factory=list)   # [(valor, texto)]
    valor: object = None
    solo_lectura: bool = False
    placeholder: str = ""
    maximo: int = 100


class FormularioDialog(QDialog):
    """Formulario genérico. `al_guardar(valores) -> (ok, mensaje)`; si falla, se muestra el error sin cerrar."""

    def __init__(self, titulo, campos, al_guardar, parent=None, texto_ok="Guardar"):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumWidth(460)
        self._campos, self._widgets, self._al_guardar = campos, {}, al_guardar
        raiz = QVBoxLayout(self)
        t = QLabel(titulo)
        t.setObjectName("TituloDialogo")
        raiz.addWidget(t)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setVerticalSpacing(10)
        for c in campos:
            w = self._crear(c)
            self._widgets[c.nombre] = w
            form.addRow(c.etiqueta + (" *" if c.requerido else ""), w)
        raiz.addLayout(form)
        nota = QLabel("* Campo obligatorio")
        nota.setObjectName("Nota")
        raiz.addWidget(nota)
        self.error = QLabel("")
        self.error.setObjectName("MensajeError")
        self.error.setWordWrap(True)
        self.error.hide()
        raiz.addWidget(self.error)
        bb = QDialogButtonBox()
        ok = bb.addButton(texto_ok, QDialogButtonBox.AcceptRole)
        ok.setProperty("variante", "primario")
        cancelar = bb.addButton("Cancelar", QDialogButtonBox.RejectRole)
        cancelar.setProperty("variante", "secundario")
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        raiz.addWidget(bb)

    def _crear(self, c: Campo):
        v = c.valor
        if c.tipo in ("texto", "password"):
            w = QLineEdit(str(v) if v not in (None, "") else "")
            w.setMaxLength(c.maximo)
            w.setPlaceholderText(c.placeholder)
            if c.tipo == "password":
                w.setEchoMode(QLineEdit.Password)
        elif c.tipo == "multilinea":
            w = QPlainTextEdit(str(v or ""))
            w.setFixedHeight(80)
        elif c.tipo == "entero":
            w = QSpinBox()
            w.setRange(0, 100000)
            w.setValue(int(v) if v not in (None, "") else 0)
        elif c.tipo in ("fecha", "fecha_req"):
            w = QDateEdit()
            w.setCalendarPopup(True)
            w.setDisplayFormat("yyyy-MM-dd")
            if c.tipo == "fecha":
                w.setMinimumDate(QDate(1900, 1, 1))
                w.setSpecialValueText("Sin fecha")
                w.setDate(QDate(v.year, v.month, v.day) if isinstance(v, date) else QDate(1900, 1, 1))
            else:
                w.setDate(QDate(v.year, v.month, v.day) if isinstance(v, date) else QDate.currentDate())
        elif c.tipo == "combo":
            w = QComboBox()
            if not c.requerido:
                w.addItem("— Sin seleccionar —", None)
            elif v is None:
                w.addItem("— Seleccione —", None)
            for valor, texto in c.opciones:
                w.addItem(str(texto), valor)
            if v is not None:
                i = w.findData(v)
                if i >= 0:
                    w.setCurrentIndex(i)
        elif c.tipo == "check":
            w = QCheckBox()
            w.setChecked(True if v is None else bool(v))
        else:
            w = QLineEdit(str(v or ""))
        if c.solo_lectura:
            w.setEnabled(False)
        return w

    def valores(self) -> dict:
        out = {}
        for c in self._campos:
            w = self._widgets[c.nombre]
            if c.tipo in ("texto", "password", "hora"):
                out[c.nombre] = w.text().strip() if c.tipo != "password" else w.text()
            elif c.tipo == "multilinea":
                out[c.nombre] = w.toPlainText().strip()
            elif c.tipo == "entero":
                out[c.nombre] = w.value()
            elif c.tipo in ("fecha", "fecha_req"):
                d = w.date()
                out[c.nombre] = None if (c.tipo == "fecha" and d == w.minimumDate()) else date(d.year(), d.month(), d.day())
            elif c.tipo == "combo":
                out[c.nombre] = w.currentData()
            elif c.tipo == "check":
                out[c.nombre] = w.isChecked()
        return out

    def accept(self):
        vals = self.valores()
        for c in self._campos:
            if c.requerido and c.tipo not in ("check", "entero") and vals[c.nombre] in (None, ""):
                self._mostrar_error(f"Complete el campo «{c.etiqueta}».")
                return
        ok, msg = self._al_guardar(vals)
        if ok:
            super().accept()
        else:
            self._mostrar_error(msg)

    def _mostrar_error(self, msg):
        self.error.setText(msg)
        self.error.show()


# ---------------- tablas ----------------
def _texto(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Sí" if v else "No"
    if isinstance(v, (date, datetime)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, time):
        return v.strftime("%H:%M")
    return str(v)


def crear_tabla():
    t = QTableWidget()
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setSelectionMode(QAbstractItemView.SingleSelection)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    t.setSortingEnabled(True)
    return t


def llenar_tabla(tabla, titulos, filas, ids=None):
    """filas: lista de listas. ids: id de cada fila (se guarda para recuperar el registro)."""
    tabla.setSortingEnabled(False)
    tabla.clear()
    tabla.setColumnCount(len(titulos))
    tabla.setHorizontalHeaderLabels(titulos)
    tabla.setRowCount(len(filas))
    for r, fila in enumerate(filas):
        for c, valor in enumerate(fila):
            txt = _texto(valor)
            item = QTableWidgetItem(txt)
            if txt in COLORES_ESTADO:
                item.setForeground(QColor(COLORES_ESTADO[txt]))
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                item.setTextAlignment(Qt.AlignCenter)
            if c == 0 and ids is not None:
                item.setData(Qt.UserRole, ids[r])
            tabla.setItem(r, c, item)
    tabla.setSortingEnabled(True)


# ---------------- tarjetas y página CRUD ----------------
class TarjetaResumen(QFrame):
    def __init__(self, titulo, valor="—", detalle=""):
        super().__init__()
        self.setObjectName("Tarjeta")
        lay = QVBoxLayout(self)
        self.titulo = QLabel(titulo)
        self.titulo.setObjectName("TarjetaTitulo")
        self.valor = QLabel(str(valor))
        self.valor.setObjectName("TarjetaValor")
        self.detalle = QLabel(detalle)
        self.detalle.setObjectName("Nota")
        for w in (self.titulo, self.valor, self.detalle):
            lay.addWidget(w)

    def actualizar(self, valor, detalle=""):
        self.valor.setText(str(valor))
        self.detalle.setText(detalle)


class PaginaCrud(QWidget):
    """Página con búsqueda, tabla y botones Nuevo / Editar / Eliminar.

    Las subclases definen: titulo, columnas [(clave, título)], cargar(texto), campos(registro),
    crear(vals), actualizar(id, vals), borrar(id)  (los tres últimos devuelven un Resultado).
    """
    titulo = ""
    columnas: list = []
    puede_crear = puede_editar = puede_eliminar = True
    texto_busqueda = "Buscar…"
    mensaje_vacio = "No hay registros para mostrar."

    def __init__(self, ctl=None, parent=None):
        super().__init__(parent)
        self.ctl = ctl
        raiz = QVBoxLayout(self)
        raiz.setSpacing(12)
        barra = QHBoxLayout()
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText(self.texto_busqueda)
        self.busqueda.setClearButtonEnabled(True)
        self.busqueda.setMinimumWidth(240)
        self._timer = QTimer(self, singleShot=True, interval=250)
        self._timer.timeout.connect(self.refrescar)
        self.busqueda.textChanged.connect(lambda _: self._timer.start())
        barra.addWidget(self.busqueda)
        for w in self.filtros_extra():
            barra.addWidget(w)
        barra.addStretch()
        self.botones = []
        if self.puede_crear:
            self.btn_nuevo = boton("＋ Nuevo", "primario")
            self.btn_nuevo.clicked.connect(self._nuevo)
            barra.addWidget(self.btn_nuevo)
        if self.puede_editar:
            self.btn_editar = boton("Editar")
            self.btn_editar.clicked.connect(self._editar)
            barra.addWidget(self.btn_editar)
        if self.puede_eliminar:
            self.btn_eliminar = boton("Eliminar", "peligro")
            self.btn_eliminar.clicked.connect(self._eliminar)
            barra.addWidget(self.btn_eliminar)
        for b in self.botones_extra():
            barra.addWidget(b)
        raiz.addLayout(barra)
        self.tabla = crear_tabla()
        if self.puede_editar:
            self.tabla.doubleClicked.connect(lambda _: self._editar())
        raiz.addWidget(self.tabla, 1)
        self.vacio = QLabel(self.mensaje_vacio)
        self.vacio.setObjectName("MensajeVacio")
        self.vacio.setAlignment(Qt.AlignCenter)
        raiz.addWidget(self.vacio)
        self.estado = QLabel("")
        self.estado.setObjectName("MensajeExito")
        raiz.addWidget(self.estado)
        self._registros = []

    # --- hooks ---
    def filtros_extra(self): return []
    def botones_extra(self): return []
    def cargar(self, texto): return None
    def campos(self, registro): return []
    def crear(self, vals): return None
    def actualizar(self, id_, vals): return None
    def borrar(self, id_): return None

    # --- lógica común ---
    def refrescar(self):
        res = self.cargar(self.busqueda.text().strip())
        if res is not None and not res.ok:
            mostrar_error(self, "No se pudo cargar la información", res.mensaje)
        self._registros = (res.datos if res is not None and res.ok else None) or []
        llenar_tabla(self.tabla, [t for _, t in self.columnas],
                     [[r.get(k) for k, _ in self.columnas] for r in self._registros],
                     [r.get("id") for r in self._registros])
        self.vacio.setVisible(not self._registros)
        self.tabla.setVisible(bool(self._registros))

    def seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        id_ = self.tabla.item(fila, 0).data(Qt.UserRole)
        return next((r for r in self._registros if r.get("id") == id_), None)

    def _exigir_seleccion(self):
        reg = self.seleccionado()
        if reg is None:
            mostrar_aviso(self, "Seleccione un registro", "Primero seleccione un registro de la tabla.")
        return reg

    def _exito(self, msg):
        self.estado.setText("✔ " + msg if msg else "")
        QTimer.singleShot(4000, lambda: self.estado.setText(""))

    def _abrir(self, titulo, campos, funcion):
        resultado = {}

        def guardar(vals):
            res = funcion(vals)
            resultado["msg"] = res.mensaje
            return res.ok, res.mensaje

        dlg = FormularioDialog(titulo, campos, guardar, self)
        if dlg.exec():
            self.refrescar()
            self._exito(resultado.get("msg", ""))

    def _nuevo(self):
        self._abrir("Nuevo registro", self.campos(None), self.crear)

    def _editar(self):
        reg = self._exigir_seleccion()
        if reg:
            self._abrir("Editar registro", self.campos(reg), lambda v: self.actualizar(reg["id"], v))

    def _eliminar(self):
        reg = self._exigir_seleccion()
        if reg and confirmar(self, "¿Desea eliminar el registro seleccionado? Esta acción no se puede deshacer."):
            res = self.borrar(reg["id"])
            if res.ok:
                self.refrescar()
                self._exito(res.mensaje)
            else:
                mostrar_aviso(self, "No se pudo eliminar", res.mensaje)


def combo(opciones, todos="Todos", datos_actual=None):
    c = QComboBox()
    c.addItem(todos, None)
    for v, t in opciones:
        c.addItem(str(t), v)
    return c
