from PySide6.QtWidgets import QComboBox

from utils.constantes import ESTADOS_MATRICULA
from views.componentes import Campo, PaginaCrud, combo


class MatriculasPage(PaginaCrud):
    columnas = [("anio", "Año"), ("codigo", "Código"), ("estudiante", "Estudiante"), ("centro", "Centro"),
                ("grado", "Grado"), ("seccion", "Sección"), ("estado", "Estado")]
    texto_busqueda = "Buscar estudiante…"

    def __init__(self, ctl, est_ctl, cat_ctl, parent=None):
        self.est_ctl, self.cat = est_ctl, cat_ctl
        super().__init__(ctl, parent)

    def _op(self, clave, activos=True): return self.cat.opciones(clave, activos).datos or []

    def filtros_extra(self):
        self.f_anio = combo(self._op("anios", False), "Todos los años")
        self.f_grado = combo(self._op("grados"), "Todos los grados")
        self.f_sec = combo(self._op("secciones"), "Todas las secciones")
        for c in (self.f_anio, self.f_grado, self.f_sec):
            c.currentIndexChanged.connect(self.refrescar)
        return [self.f_anio, self.f_grado, self.f_sec]

    def cargar(self, texto):
        return self.ctl.listar(texto, self.f_anio.currentData(), self.f_grado.currentData(), self.f_sec.currentData())

    def campos(self, r):
        nuevo = r is None
        r = r or {}
        actual = self.cat.anio_actual().datos
        return [Campo("id_estudiante", "Estudiante", "combo", True, self.est_ctl.opciones().datos or [],
                      r.get("id_estudiante"), solo_lectura=not nuevo),
                Campo("id_anio", "Año lectivo", "combo", True, self._op("anios", nuevo),
                      r.get("id_anio") or (actual[0] if actual else None), solo_lectura=not nuevo),
                Campo("id_centro", "Centro educativo", "combo", True, self._op("centros"), r.get("id_centro")),
                Campo("id_grado", "Grado", "combo", True, self._op("grados"), r.get("id_grado")),
                Campo("id_seccion", "Sección", "combo", True, self._op("secciones"), r.get("id_seccion")),
                Campo("estado", "Estado", "combo", True, [(e, e.capitalize()) for e in ESTADOS_MATRICULA],
                      r.get("estado") or "activa")]

    def crear(self, v): return self.ctl.crear(v)
    def actualizar(self, id_, v): return self.ctl.actualizar(id_, v)
    def borrar(self, id_): return self.ctl.eliminar(id_)
