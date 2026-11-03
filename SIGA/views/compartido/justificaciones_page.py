from PySide6.QtWidgets import QComboBox

from utils.constantes import ESTADOS_JUSTIFICACION
from views.componentes import Campo, FormularioDialog, PaginaCrud, boton, combo, mostrar_aviso


class JustificacionesPage(PaginaCrud):
    columnas = [("fecha", "Fecha falta"), ("estudiante", "Estudiante"), ("grupo", "Grupo"),
                ("asignatura", "Asignatura"), ("estado", "Falta"), ("motivo", "Motivo"),
                ("estado_just", "Estado"), ("comentario_revision", "Comentario de revisión")]
    puede_crear = puede_editar = puede_eliminar = False
    texto_busqueda = "Buscar por estudiante o motivo…"
    mensaje_vacio = "No hay justificaciones para mostrar."

    def __init__(self, ctl, actor, parent=None):
        self.actor = actor
        super().__init__(ctl, parent)

    def filtros_extra(self):
        self.f_estado = combo([(e, e.capitalize()) for e in ESTADOS_JUSTIFICACION], "Todos los estados")
        self.f_estado.currentIndexChanged.connect(self.refrescar)
        return [self.f_estado]

    def botones_extra(self):
        out = []
        if self.actor.tiene("justificaciones.registrar"):
            b = boton("＋ Registrar justificación", "primario")
            b.clicked.connect(self._registrar)
            out.append(b)
        if self.actor.tiene("justificaciones.revisar"):
            a = boton("Aprobar")
            a.clicked.connect(lambda: self._resolver(True))
            r = boton("Rechazar", "peligro")
            r.clicked.connect(lambda: self._resolver(False))
            out += [a, r]
        return out

    def cargar(self, texto):
        res = self.ctl.listar(self.f_estado.currentData())
        if res.ok and texto:
            t = texto.lower()
            res.datos = [f for f in res.datos if t in f"{f['estudiante']} {f['motivo']}".lower()]
        return res

    def _registrar(self):
        pend = self.ctl.sin_justificar()
        if not pend.ok or not pend.datos:
            mostrar_aviso(self, "Sin ausencias pendientes",
                          pend.mensaje or "No hay ausencias o tardanzas sin justificar.")
            return
        opciones = [(f["id_asistencia"], f["texto"]) for f in pend.datos]

        def guardar(v):
            res = self.ctl.registrar(v["id_asistencia"], v["motivo"])
            return res.ok, res.mensaje

        dlg = FormularioDialog("Registrar justificación", [
            Campo("id_asistencia", "Ausencia o tardanza", "combo", True, opciones),
            Campo("motivo", "Motivo", "multilinea", True)], guardar, self)
        if dlg.exec():
            self.refrescar()
            self._exito("Justificación registrada.")

    def _resolver(self, aprobar):
        r = self._exigir_seleccion()
        if not r:
            return
        if r["estado_just"] != "pendiente":
            mostrar_aviso(self, "Justificación ya revisada", "Solo se pueden revisar justificaciones pendientes.")
            return

        def guardar(v):
            res = self.ctl.resolver(r["id"], aprobar, v["comentario"])
            return res.ok, res.mensaje

        dlg = FormularioDialog("Aprobar justificación" if aprobar else "Rechazar justificación", [
            Campo("comentario", "Comentario" + ("" if aprobar else " (obligatorio)"), "multilinea",
                  not aprobar)], guardar, self, "Aprobar" if aprobar else "Rechazar")
        if dlg.exec():
            self.refrescar()
            self._exito("Justificación aprobada." if aprobar else "Justificación rechazada.")
