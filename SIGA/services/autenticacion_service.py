from datetime import datetime, timedelta

from config import settings
from database.connection import get_session
from models import Usuario
from repositories.usuario_repository import UsuarioRepository
from services import auditoria_service
from services.permisos_service import UsuarioActual, requerir_autenticado
from utils.excepciones import AutenticacionError
from utils.seguridad import hash_password, validar_fortaleza, verificar_password
from utils.excepciones import ValidacionError

MSG_INVALIDAS = "Credenciales inválidas. Verifique su usuario y contraseña."


def construir_actor(usuario: Usuario) -> UsuarioActual:
    permisos = {p.codigo for r in usuario.roles for p in r.permisos}
    if usuario.profesor:
        nombre = usuario.profesor.nombre_completo
    elif usuario.estudiante:
        nombre = usuario.estudiante.nombre_completo
    else:
        nombre = usuario.username
    return UsuarioActual(
        id_usuario=usuario.id_usuario, username=usuario.username, nombre=nombre,
        roles=[r.nombre for r in usuario.roles], permisos=permisos,
        id_profesor=usuario.id_profesor, id_estudiante=usuario.id_estudiante,
        debe_cambiar_password=usuario.debe_cambiar_password)


def iniciar_sesion(username: str, password: str) -> UsuarioActual:
    username = (username or "").strip()
    if not username or not password:
        raise AutenticacionError("Ingrese su usuario y contraseña.")
    error, actor = None, None
    with get_session() as s:
        u = UsuarioRepository(s).por_username(username)
        ahora = datetime.now()
        if u is None:
            auditoria_service.registrar(s, None, "LOGIN_FALLIDO", "usuario", None,
                                        "Usuario inexistente", username=username[:50])
            error = MSG_INVALIDAS
        elif u.bloqueado_hasta and u.bloqueado_hasta > ahora:
            minutos = int((u.bloqueado_hasta - ahora).total_seconds() // 60) + 1
            error = f"Cuenta bloqueada temporalmente por intentos fallidos. Intente en {minutos} minuto(s)."
        elif not verificar_password(password, u.password_hash):
            u.intentos_fallidos = (u.intentos_fallidos or 0) + 1
            detalle = f"Intento fallido {u.intentos_fallidos}"
            if u.intentos_fallidos >= settings.MAX_INTENTOS_LOGIN:
                u.bloqueado_hasta = ahora + timedelta(minutes=settings.MINUTOS_BLOQUEO)
                u.intentos_fallidos = 0
                detalle += " (cuenta bloqueada)"
            auditoria_service.registrar(s, None, "LOGIN_FALLIDO", "usuario", u.id_usuario, detalle,
                                        username=u.username)
            error = MSG_INVALIDAS
        elif not u.activo:
            error = "Su cuenta está desactivada. Contacte al administrador."
        else:
            u.intentos_fallidos, u.bloqueado_hasta, u.ultimo_acceso = 0, None, ahora
            actor = construir_actor(u)
            if not actor.roles:
                actor, error = None, "Su cuenta no tiene un rol asignado. Contacte al administrador."
            else:
                auditoria_service.registrar(s, actor, "LOGIN", "usuario", u.id_usuario, "Inicio de sesión")
    if error:
        raise AutenticacionError(error)
    return actor


def cambiar_password(actor, actual: str, nueva: str, confirmar: str):
    requerir_autenticado(actor)
    if nueva != confirmar:
        raise ValidacionError("La confirmación no coincide con la nueva contraseña.")
    validar_fortaleza(nueva)
    with get_session() as s:
        u = s.get(Usuario, actor.id_usuario)
        if not verificar_password(actual or "", u.password_hash):
            raise AutenticacionError("La contraseña actual es incorrecta.")
        if verificar_password(nueva, u.password_hash):
            raise ValidacionError("La nueva contraseña debe ser distinta de la actual.")
        u.password_hash = hash_password(nueva)
        u.debe_cambiar_password = False
        auditoria_service.registrar(s, actor, "CAMBIO_PASSWORD", "usuario", u.id_usuario)
    actor.debe_cambiar_password = False


def perfil(actor) -> dict:
    requerir_autenticado(actor)
    with get_session() as s:
        u = s.get(Usuario, actor.id_usuario)
        datos = {"Usuario": u.username, "Rol": actor.rol_principal, "Nombre": actor.nombre}
        if u.profesor:
            p = u.profesor
            datos.update({"Cédula": p.cedula, "Código MINED": p.codigo_mined,
                          "Teléfono": p.telefono or "—", "Especialidad": p.especialidad or "—",
                          "Nivel académico": p.nivel_academico or "—",
                          "Centro": p.centro.nombre if p.centro else "—",
                          "Turno": p.turno.nombre if p.turno else "—"})
        elif u.estudiante:
            e = u.estudiante
            datos.update({"Código estudiantil": e.codigo, "Cédula": e.cedula or "—",
                          "Teléfono": e.telefono or "—", "Correo": e.correo or "—"})
        datos["Último acceso"] = u.ultimo_acceso.strftime("%Y-%m-%d %H:%M") if u.ultimo_acceso else "—"
        return datos
