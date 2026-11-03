from PySide6.QtWidgets import QApplication

from utils.constantes import ROL_ADMIN, ROL_DOCENTE, ROL_ESTUDIANTE
from views.componentes import Campo, FormularioDialog, PaginaCrud, boton, confirmar, mostrar_aviso, mostrar_info

ROLES = [(r, r) for r in (ROL_ADMIN, ROL_DOCENTE, ROL_ESTUDIANTE)]


class UsuariosPage(PaginaCrud):
    columnas = [("username", "Usuario"), ("roles", "Rol"), ("vinculo", "Vinculado a"), ("activo", "Activo"),
                ("ultimo_acceso", "Último acceso")]
    puede_editar = puede_eliminar = False
    texto_busqueda = "Buscar usuario…"

    def botones_extra(self):
        self.b_estado = boton("Activar / Desactivar")
        self.b_estado.clicked.connect(self._estado)
        self.b_rol = boton("Cambiar rol")
        self.b_rol.clicked.connect(self._rol)
        self.b_reset = boton("Restablecer contraseña")
        self.b_reset.clicked.connect(self._reset)
        return [self.b_estado, self.b_rol, self.b_reset]

    def cargar(self, texto): return self.ctl.listar(texto)

    def campos(self, r):
        return [Campo("username", "Usuario", requerido=True, maximo=50),
                Campo("password", "Contraseña inicial", "password", True, placeholder="Mínimo 8, letras y números"),
                Campo("rol", "Rol", "combo", True, ROLES),
                Campo("id_profesor", "Profesor vinculado (rol Docente)", "combo", False, self.ctl.profesores_libres().datos or []),
                Campo("id_estudiante", "Estudiante vinculado (rol Estudiante)", "combo", False, self.ctl.estudiantes_libres().datos or [])]

    def crear(self, v): return self.ctl.crear(v)

    def _estado(self):
        r = self._exigir_seleccion()
        if r:
            nuevo = not r["activo"]
            if confirmar(self, f"¿{'Activar' if nuevo else 'Desactivar'} la cuenta «{r['username']}»?"):
                res = self.ctl.estado(r["id"], nuevo)
                self.refrescar() if res.ok else mostrar_aviso(self, "No se pudo cambiar el estado", res.mensaje)

    def _rol(self):
        r = self._exigir_seleccion()
        if not r:
            return
        def guardar(v):
            res = self.ctl.asignar_rol(r["id"], v["rol"])
            return res.ok, res.mensaje
        dlg = FormularioDialog(f"Cambiar rol de {r['username']}",
                            [Campo("rol", "Nuevo rol", "combo", True, ROLES, r["rol"])], guardar, self)
        if dlg.exec():
            self.refrescar()

    def _reset(self):
        r = self._exigir_seleccion()
        if r and confirmar(self, f"¿Restablecer la contraseña de «{r['username']}»?"):
            res = self.ctl.restablecer(r["id"])
            if res.ok:
                mostrar_info(self, "Contraseña restablecida",
                            f"Contraseña temporal para «{r['username']}»:\n\n{res.datos}\n\n"
                            "Entréguela al usuario por un medio seguro. Deberá cambiarla al ingresar.")
            else:
                mostrar_aviso(self, "No se pudo restablecer", res.mensaje)
