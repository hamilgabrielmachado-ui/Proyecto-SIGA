from views.componentes import PaginaCrud


class HorarioPage(PaginaCrud):
    puede_crear = puede_editar = puede_eliminar = False
    texto_busqueda = "Buscar por asignatura, grupo o día…"
    mensaje_vacio = "No hay clases asignadas para mostrar."

    def __init__(self, ctl, modo, parent=None):
        self.columnas = [("dia", "Día"), ("periodo", "Periodo"), ("horario", "Horario"), ("asignatura", "Asignatura"),
                         ("grupo", "Grupo"), ("modalidad", "Modalidad"), ("centro", "Centro")]
        if modo == "estudiante":
            self.columnas.insert(5, ("profesor", "Docente"))
        super().__init__(ctl, parent)

    def cargar(self, texto):
        res = self.ctl.mi_horario()
        if res.ok and texto:
            t = texto.lower()
            res.datos = [f for f in res.datos if t in f"{f['asignatura']} {f['grupo']} {f['dia']}".lower()]
        return res
