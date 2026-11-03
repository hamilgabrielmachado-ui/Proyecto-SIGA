from PySide6.QtWidgets import QComboBox

from utils.constantes import SEXOS
from views.componentes import Campo, PaginaCrud


class EstudiantesPage(PaginaCrud):
    columnas = [("codigo", "Código"), ("nombre", "Estudiante"), ("sexo", "Sexo"), ("fecha_nacimiento", "Nacimiento"),
                ("cedula", "Cédula"), ("telefono", "Teléfono"), ("activo", "Activo")]
    texto_busqueda = "Buscar por nombre, código o cédula…"

    def filtros_extra(self):
        self.filtro = QComboBox()
        for t, v in (("Todos", None), ("Activos", True), ("Inactivos", False)):
            self.filtro.addItem(t, v)
        self.filtro.currentIndexChanged.connect(self.refrescar)
        return [self.filtro]

    def cargar(self, texto): return self.ctl.listar(texto, self.filtro.currentData())

    def campos(self, r):
        r = r or {}
        return [Campo("codigo", "Código estudiantil", requerido=True, valor=r.get("codigo"), maximo=30),
                Campo("cedula", "Cédula", valor=r.get("cedula"), maximo=20),
                Campo("nombres", "Nombres", requerido=True, valor=r.get("nombres")),
                Campo("apellidos", "Apellidos", requerido=True, valor=r.get("apellidos")),
                Campo("fecha_nacimiento", "Fecha de nacimiento", "fecha", valor=r.get("fecha_nacimiento")),
                Campo("sexo", "Sexo", "combo", True, list(SEXOS.items()), r.get("sexo")),
                Campo("telefono", "Teléfono", valor=r.get("telefono"), maximo=20),
                Campo("correo", "Correo electrónico", valor=r.get("correo"), maximo=120),
                Campo("activo", "Activo", "check", valor=r.get("activo"))]

    def crear(self, v): return self.ctl.crear(v)
    def actualizar(self, id_, v): return self.ctl.actualizar(id_, v)
    def borrar(self, id_): return self.ctl.eliminar(id_)
