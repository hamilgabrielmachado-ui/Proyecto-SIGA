from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
                               QVBoxLayout, QWidget)

from controllers.asignacion_controller import AsignacionController
from controllers.asistencia_controller import AsistenciaController
from controllers.catalogo_controller import CatalogoController
from controllers.estudiante_controller import EstudianteController
from controllers.justificacion_controller import JustificacionController
from controllers.matricula_controller import MatriculaController
from controllers.profesor_controller import ProfesorController
from controllers.reportes_controller import ReportesController
from controllers.sistema_controller import SistemaController
from controllers.usuario_controller import UsuarioController
from utils.constantes import ROL_ADMIN, ROL_DOCENTE, ROL_ESTUDIANTE
from views.admin.asignaciones_page import AsignacionesPage
from views.admin.auditoria_page import AuditoriaPage
from views.admin.catalogos_page import CatalogosPage
from views.admin.dashboard_admin import DashboardAdmin
from views.admin.estudiantes_page import EstudiantesPage
from views.admin.matriculas_page import MatriculasPage
from views.admin.profesores_page import ProfesoresPage
from views.admin.usuarios_page import UsuariosPage
from views.compartido.asistencia_page import AsistenciaConsultaPage, AsistenciaRegistroPage
from views.compartido.horario_page import HorarioPage
from views.compartido.justificaciones_page import JustificacionesPage
from views.compartido.perfil_page import PerfilPage
from views.compartido.reportes_page import ReportesPage
from views.componentes import confirmar
from views.docente.dashboard_docente import DashboardDocente
from views.estudiante.dashboard_estudiante import DashboardEstudiante


def construir_modulos(actor):
    """Lista de (clave, título, ícono, fábrica) según el rol. La seguridad real está en los servicios."""
    sis = SistemaController(actor)
    asi, jus = AsistenciaController(actor), JustificacionController(actor)
    perfil = ("perfil", "Mi perfil", "◉", lambda: PerfilPage(sis))
    if actor.rol_principal == ROL_ADMIN:
        cat = CatalogoController(actor)
        return [
            ("inicio", "Inicio", "⌂", lambda: DashboardAdmin(sis)),
            ("estudiantes", "Estudiantes", "☺", lambda: EstudiantesPage(EstudianteController(actor))),
            ("profesores", "Profesores", "✎", lambda: ProfesoresPage(ProfesorController(actor))),
            ("catalogos", "Centros y catálogos", "▤", lambda: CatalogosPage(cat)),
            ("matriculas", "Matrículas", "✔", lambda: MatriculasPage(MatriculaController(actor), EstudianteController(actor), cat)),
            ("asignaciones", "Asignaciones", "☰", lambda: AsignacionesPage(AsignacionController(actor), ProfesorController(actor), cat)),
            ("asistencia", "Registrar asistencia", "✓", lambda: AsistenciaRegistroPage(asi)),
            ("consulta", "Consultar asistencia", "⌕", lambda: AsistenciaConsultaPage(asi)),
            ("justificaciones", "Justificaciones", "✉", lambda: JustificacionesPage(jus, actor)),
            ("reportes", "Reportes", "▥", lambda: ReportesPage(ReportesController(actor))),
            ("usuarios", "Usuarios y roles", "⚿", lambda: UsuariosPage(UsuarioController(actor))),
            ("auditoria", "Auditoría y respaldos", "☷", lambda: AuditoriaPage(sis)),
            perfil]
    if actor.rol_principal == ROL_DOCENTE:
        return [
            ("inicio", "Inicio", "⌂", lambda: DashboardDocente(sis)),
            ("horario", "Mis grupos y horario", "☰", lambda: HorarioPage(AsignacionController(actor), "docente")),
            ("asistencia", "Registrar asistencia", "✓", lambda: AsistenciaRegistroPage(asi)),
            ("consulta", "Consultar asistencia", "⌕", lambda: AsistenciaConsultaPage(asi)),
            ("justificaciones", "Justificaciones", "✉", lambda: JustificacionesPage(jus, actor)),
            ("reportes", "Reportes", "▥", lambda: ReportesPage(ReportesController(actor))),
            perfil]
    return [
        ("inicio", "Inicio", "⌂", lambda: DashboardEstudiante(sis)),
        ("horario", "Mi horario", "☰", lambda: HorarioPage(AsignacionController(actor), "estudiante")),
        ("consulta", "Mi asistencia", "⌕", lambda: AsistenciaConsultaPage(asi)),
        ("justificaciones", "Mis justificaciones", "✉", lambda: JustificacionesPage(jus, actor)),
        perfil]


class MainWindow(QMainWindow):
    sesion_cerrada = Signal()

    def __init__(self, actor):
        super().__init__()
        self.actor = actor
        self.setWindowTitle("SIGA — Sistema Integral de Gestión de Asistencia Escolar")
        self.setMinimumSize(1000, 640)
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QHBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # --- menú lateral ---
        lateral = QFrame()
        lateral.setObjectName("Sidebar")
        lateral.setFixedWidth(230)
        ll = QVBoxLayout(lateral)
        ll.setContentsMargins(12, 16, 12, 12)
        ll.setSpacing(4)
        marca = QLabel("SIGA")
        marca.setObjectName("SidebarMarca")
        ll.addWidget(marca)
        ll.addSpacing(10)
        self.grupo = QButtonGroup(self)
        self.grupo.setExclusive(True)
        self.paginas, self.fabricas, self.titulos = {}, {}, {}
        self.pila = QStackedWidget()
        for clave, titulo, icono, fabrica in construir_modulos(actor):
            b = QPushButton(f"  {icono}   {titulo}")
            b.setCheckable(True)
            b.setObjectName("MenuBoton")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=clave: self.ir_a(k))
            self.grupo.addButton(b)
            ll.addWidget(b)
            self.fabricas[clave], self.titulos[clave], self.paginas[clave] = fabrica, titulo, None
            setattr(self, f"_btn_{clave}", b)
        ll.addStretch()
        salir = QPushButton("  ⏻   Cerrar sesión")
        salir.setObjectName("MenuSalir")
        salir.setCursor(Qt.PointingHandCursor)
        salir.clicked.connect(self.cerrar_sesion)
        ll.addWidget(salir)
        raiz.addWidget(lateral)

        # --- zona derecha ---
        der = QVBoxLayout()
        der.setSpacing(0)
        barra = QFrame()
        barra.setObjectName("Topbar")
        bl = QHBoxLayout(barra)
        bl.setContentsMargins(24, 10, 24, 10)
        self.titulo = QLabel("")
        self.titulo.setObjectName("TopbarTitulo")
        bl.addWidget(self.titulo)
        bl.addStretch()
        nombre = QLabel(actor.nombre)
        nombre.setObjectName("TopbarUsuario")
        rol = QLabel(actor.rol_principal)
        rol.setObjectName("InsigniaRol")
        perfil_btn = QPushButton("Mi perfil")
        perfil_btn.setProperty("variante", "secundario")
        perfil_btn.clicked.connect(lambda: self.ir_a("perfil"))
        for w in (nombre, rol, perfil_btn):
            bl.addWidget(w)
        der.addWidget(barra)
        contenedor = QWidget()
        cl = QVBoxLayout(contenedor)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.addWidget(self.pila)
        der.addWidget(contenedor, 1)
        raiz.addLayout(der, 1)
        self.ir_a("inicio")

    def ir_a(self, clave):
        if clave not in self.paginas:
            return
        if self.paginas[clave] is None:
            pagina = self.fabricas[clave]()
            if hasattr(pagina, "ir_a"):
                pagina.ir_a.connect(self.ir_a)
            self.paginas[clave] = pagina
            self.pila.addWidget(pagina)
        pagina = self.paginas[clave]
        self.pila.setCurrentWidget(pagina)
        self.titulo.setText(self.titulos[clave])
        getattr(self, f"_btn_{clave}").setChecked(True)
        if hasattr(pagina, "refrescar"):
            pagina.refrescar()

    def cerrar_sesion(self):
        if confirmar(self, "¿Desea cerrar la sesión?", "Cerrar sesión"):
            self.sesion_cerrada.emit()
            self.close()
