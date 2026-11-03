from database.connection import get_session
from models import Usuario
from repositories.usuario_repository import UsuarioRepository
from services import auditoria_service
from services.permisos_service import requerir
from utils.constantes import ROL_ADMIN, ROL_DOCENTE, ROL_ESTUDIANTE
from utils.excepciones import DuplicadoError, NoEncontradoError, ValidacionError
from utils.seguridad import generar_password_temporal, hash_password, validar_fortaleza
from utils.validaciones import validar_nombre_usuario


def _fila(u):
    if u.profesor:
        vinculo = f"Profesor: {u.profesor.nombre_completo}"
    elif u.estudiante:
        vinculo = f"Estudiante: {u.estudiante.nombre_completo}"
    else:
        vinculo = "—"
    return {"id": u.id_usuario, "username": u.username, "roles": ", ".join(r.nombre for r in u.roles),
            "rol": u.roles[0].nombre if u.roles else "", "vinculo": vinculo, "activo": u.activo,
            "ultimo_acceso": u.ultimo_acceso.strftime("%Y-%m-%d %H:%M") if u.ultimo_acceso else "Nunca"}


def listar(actor, buscar=""):
    requerir(actor, "usuarios.gestionar")
    with get_session() as s:
        return [_fila(u) for u in UsuarioRepository(s).listar(buscar)]


def profesores_sin_usuario(actor):
    requerir(actor, "usuarios.gestionar")
    with get_session() as s:
        return [(p.id_profesor, f"{p.apellidos}, {p.nombres}") for p in UsuarioRepository(s).profesores_sin_usuario()]


def estudiantes_sin_usuario(actor):
    requerir(actor, "usuarios.gestionar")
    with get_session() as s:
        return [(e.id_estudiante, f"{e.apellidos}, {e.nombres} ({e.codigo})")
                for e in UsuarioRepository(s).estudiantes_sin_usuario()]


def _validar_vinculo(rol, id_profesor, id_estudiante):
    if rol == ROL_DOCENTE and not id_profesor:
        raise ValidacionError("Un usuario Docente debe estar vinculado a un profesor.")
    if rol == ROL_ESTUDIANTE and not id_estudiante:
        raise ValidacionError("Un usuario Estudiante debe estar vinculado a un estudiante.")
    if rol == ROL_ADMIN and (id_profesor or id_estudiante):
        raise ValidacionError("Un Administrador no se vincula a un profesor ni a un estudiante.")
    if id_profesor and id_estudiante:
        raise ValidacionError("Un usuario no puede vincularse a la vez con profesor y estudiante.")


def crear(actor, datos: dict):
    requerir(actor, "usuarios.gestionar")
    username = validar_nombre_usuario(datos.get("username"))
    password = datos.get("password") or ""
    validar_fortaleza(password)
    if password.lower() == username.lower():
        raise ValidacionError("La contraseña no puede ser igual al nombre de usuario.")
    rol_nombre = datos.get("rol")
    id_prof, id_est = datos.get("id_profesor"), datos.get("id_estudiante")
    _validar_vinculo(rol_nombre, id_prof, id_est)
    with get_session() as s:
        repo = UsuarioRepository(s)
        if repo.por_username(username):
            raise DuplicadoError("Ya existe un usuario con ese nombre.")
        rol = repo.rol_por_nombre(rol_nombre)
        if rol is None:
            raise ValidacionError("Seleccione un rol válido.")
        u = Usuario(username=username, password_hash=hash_password(password), activo=True,
                    debe_cambiar_password=True, id_profesor=id_prof, id_estudiante=id_est)
        u.roles.append(rol)
        repo.agregar(u)
        auditoria_service.registrar(s, actor, "USUARIO_CREADO", "usuario", u.id_usuario,
                                    f"{username} con rol {rol_nombre}")
        return {"id": u.id_usuario}


def _obtener(s, id_usuario):
    u = s.get(Usuario, id_usuario)
    if u is None:
        raise NoEncontradoError("El usuario seleccionado ya no existe.")
    return u


def cambiar_estado(actor, id_usuario, activo: bool):
    requerir(actor, "usuarios.gestionar")
    if id_usuario == actor.id_usuario and not activo:
        raise ValidacionError("No puede desactivar su propia cuenta.")
    with get_session() as s:
        u = _obtener(s, id_usuario)
        u.activo = activo
        auditoria_service.registrar(s, actor, "USUARIO_ACTIVADO" if activo else "USUARIO_DESACTIVADO",
                                    "usuario", u.id_usuario, u.username)


def restablecer_password(actor, id_usuario) -> str:
    """Genera una contraseña temporal; el usuario deberá cambiarla en su próximo inicio de sesión."""
    requerir(actor, "usuarios.gestionar")
    temporal = generar_password_temporal()
    with get_session() as s:
        u = _obtener(s, id_usuario)
        u.password_hash = hash_password(temporal)
        u.debe_cambiar_password = True
        u.intentos_fallidos, u.bloqueado_hasta = 0, None
        auditoria_service.registrar(s, actor, "PASSWORD_RESTABLECIDA", "usuario", u.id_usuario, u.username)
    return temporal


def asignar_rol(actor, id_usuario, rol_nombre):
    requerir(actor, "usuarios.gestionar")
    with get_session() as s:
        repo = UsuarioRepository(s)
        u = _obtener(s, id_usuario)
        _validar_vinculo(rol_nombre, u.id_profesor, u.id_estudiante)
        rol = repo.rol_por_nombre(rol_nombre)
        if rol is None:
            raise ValidacionError("Seleccione un rol válido.")
        if id_usuario == actor.id_usuario and rol_nombre != ROL_ADMIN:
            raise ValidacionError("No puede quitarse a sí mismo el rol de administrador.")
        anterior = ", ".join(r.nombre for r in u.roles)
        u.roles = [rol]
        auditoria_service.registrar(s, actor, "CAMBIO_PERMISOS", "usuario", u.id_usuario,
                                    f"{u.username}: {anterior} → {rol_nombre}")
