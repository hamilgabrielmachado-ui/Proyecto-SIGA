from PySide6.QtWidgets import QComboBox

from utils.constantes import NIVELES_ACADEMICOS
from views.componentes import Campo, PaginaCrud


class ProfesoresPage(PaginaCrud):
    columnas = [("nombre", "Profesor"), ("cedula", "Cédula"), ("codigo_mined", "Código MINED"),
                ("especialidad", "Especialidad"), ("nivel_academico", "Nivel"), ("centro", "Centro"),
                ("turno", "Turno"), ("anios_experiencia", "Años exp."), ("activo", "Activo")]
    texto_busqueda = "Buscar por nombre, cédula o código MINED…"

    def filtros_extra(self):
        self.filtro = QComboBox()
        for t, v in (("Todos", None), ("Activos", True), ("Inactivos", False)):
            self.filtro.addItem(t, v)
        self.filtro.currentIndexChanged.connect(self.refrescar)
        return [self.filtro]

    def cargar(self, texto): return self.ctl.listar(texto, self.filtro.currentData())

    def campos(self, r):
        r = r or {}
        centros = self.ctl.catalogo("centros").datos or []
        turnos = self.ctl.catalogo("turnos").datos or []
        return [Campo("nombres", "Nombres", requerido=True, valor=r.get("nombres")),
                Campo("apellidos", "Apellidos", requerido=True, valor=r.get("apellidos")),
                Campo("cedula", "Cédula", requerido=True, valor=r.get("cedula"), maximo=20),
                Campo("codigo_mined", "Código MINED", requerido=True, valor=r.get("codigo_mined"), maximo=30),
                Campo("telefono", "Teléfono", valor=r.get("telefono"), maximo=20),
                Campo("especialidad", "Especialidad principal", valor=r.get("especialidad")),
                Campo("nivel_academico", "Nivel académico", "combo", False,
                      [(n, n) for n in NIVELES_ACADEMICOS], r.get("nivel_academico")),
                Campo("id_centro", "Centro educativo", "combo", False, centros, r.get("id_centro")),
                Campo("id_turno", "Turno", "combo", False, turnos, r.get("id_turno")),
                Campo("anios_experiencia", "Años de experiencia", "entero", valor=r.get("anios_experiencia")),
                Campo("activo", "Activo", "check", valor=r.get("activo"))]

    def crear(self, v): return self.ctl.crear(v)
    def actualizar(self, id_, v): return self.ctl.actualizar(id_, v)
    def borrar(self, id_): return self.ctl.eliminar(id_)
