from utils.constantes import DIAS_SEMANA
from views.componentes import Campo, PaginaCrud


class AsignacionesPage(PaginaCrud):
    columnas = [("anio", "Año"), ("profesor", "Profesor"), ("grupo", "Grupo"), ("asignatura", "Asignatura"),
                ("dia", "Día"), ("periodo", "Periodo"), ("horario", "Horario"), ("modalidad", "Modalidad"),
                ("centro", "Centro")]
    texto_busqueda = "Buscar por profesor, asignatura o grado…"

    def __init__(self, ctl, prof_ctl, cat_ctl, parent=None):
        self.prof, self.cat = prof_ctl, cat_ctl
        super().__init__(ctl, parent)

    def _op(self, clave, activos=True): return self.cat.opciones(clave, activos).datos or []

    def cargar(self, texto): return self.ctl.listar(texto)

    def campos(self, r):
        r = r or {}
        actual = self.cat.anio_actual().datos
        return [Campo("id_profesor", "Profesor", "combo", True, self.prof.opciones().datos or [], r.get("id_profesor")),
                Campo("id_centro", "Centro educativo", "combo", True, self._op("centros"), r.get("id_centro")),
                Campo("id_anio", "Año lectivo", "combo", True, self._op("anios"),
                      r.get("id_anio") or (actual[0] if actual else None)),
                Campo("id_grado", "Grado", "combo", True, self._op("grados"), r.get("id_grado")),
                Campo("id_seccion", "Sección", "combo", True, self._op("secciones"), r.get("id_seccion")),
                Campo("id_asignatura", "Asignatura", "combo", True, self._op("asignaturas"), r.get("id_asignatura")),
                Campo("dia_semana", "Día de la semana", "combo", True, list(DIAS_SEMANA.items()), r.get("dia_semana")),
                Campo("id_periodo", "Periodo de clase", "combo", True, self._op("periodos"), r.get("id_periodo")),
                Campo("id_modalidad", "Modalidad", "combo", True, self._op("modalidades"), r.get("id_modalidad"))]

    def crear(self, v): return self.ctl.crear(v)
    def actualizar(self, id_, v): return self.ctl.actualizar(id_, v)
    def borrar(self, id_): return self.ctl.eliminar(id_)
