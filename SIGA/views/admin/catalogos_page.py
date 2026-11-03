from PySide6.QtWidgets import QComboBox

from views.componentes import Campo, PaginaCrud


class CatalogosPage(PaginaCrud):
    texto_busqueda = "Buscar en el catálogo…"

    def filtros_extra(self):
        self.selector = QComboBox()
        for clave, d in self.ctl.definiciones().items():
            self.selector.addItem(d.etiqueta, clave)
        self.selector.currentIndexChanged.connect(self.refrescar)
        return [self.selector]

    @property
    def clave(self): return self.selector.currentData()

    def cargar(self, texto):
        d = self.ctl.definiciones()[self.clave]
        self.columnas = [(a, e) for a, e, _, _ in d.campos] + [("activo", "Activo")]
        return self.ctl.listar(self.clave, texto)

    def campos(self, r):
        r = r or {}
        d = self.ctl.definiciones()[self.clave]
        tipos = {"texto": "texto", "entero": "entero", "hora": "texto"}
        return [Campo(a, e, tipos[t], req, valor=r.get(a), placeholder="HH:MM" if t == "hora" else "")
                for a, e, t, req in d.campos] + [Campo("activo", "Activo", "check", valor=r.get("activo"))]

    def crear(self, v): return self.ctl.crear(self.clave, v)
    def actualizar(self, id_, v): return self.ctl.actualizar(self.clave, id_, v)
    def borrar(self, id_): return self.ctl.eliminar(self.clave, id_)
