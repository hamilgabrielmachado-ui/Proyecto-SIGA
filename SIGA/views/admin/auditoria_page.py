from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QLabel

from views.componentes import PaginaCrud, boton, mostrar_aviso, mostrar_info
from datetime import date


class AuditoriaPage(PaginaCrud):
    columnas = [("fecha", "Fecha y hora"), ("usuario", "Usuario"), ("accion", "Acción"), ("entidad", "Entidad"),
                ("id_entidad", "ID"), ("detalle", "Detalle")]
    puede_crear = puede_editar = puede_eliminar = False
    texto_busqueda = "Buscar por usuario, acción o detalle…"

    def filtros_extra(self):
        self.desde = QDateEdit(QDate.currentDate().addDays(-30))
        self.hasta = QDateEdit(QDate.currentDate())
        for d in (self.desde, self.hasta):
            d.setCalendarPopup(True)
            d.setDisplayFormat("yyyy-MM-dd")
            d.dateChanged.connect(self.refrescar)
        return [QLabel("Desde"), self.desde, QLabel("Hasta"), self.hasta]

    def botones_extra(self):
        b = boton("Crear respaldo de la base de datos", "primario")
        b.clicked.connect(self._respaldo)
        return [b]

    def _fecha(self, w):
        d = w.date()
        return date(d.year(), d.month(), d.day())

    def cargar(self, texto):
        return self.ctl.auditoria(texto, self._fecha(self.desde), self._fecha(self.hasta))

    def _respaldo(self):
        res = self.ctl.respaldo()
        if res.ok:
            mostrar_info(self, "Respaldo creado", f"Respaldo guardado en:\n{res.datos}")
            self.refrescar()
        else:
            mostrar_aviso(self, "No se pudo crear el respaldo", res.mensaje)
