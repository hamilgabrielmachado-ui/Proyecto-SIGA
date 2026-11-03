"""Usuario autenticado y verificación de permisos (se aplica en cada servicio)."""
from dataclasses import dataclass, field

from utils.constantes import ROL_ADMIN, ROL_DOCENTE, ROL_ESTUDIANTE
from utils.excepciones import PermisoError


@dataclass
class UsuarioActual:
    id_usuario: int
    username: str
    nombre: str
    roles: list = field(default_factory=list)
    permisos: set = field(default_factory=set)
    id_profesor: int | None = None
    id_estudiante: int | None = None
    debe_cambiar_password: bool = False

    @property
    def es_admin(self):
        return ROL_ADMIN in self.roles

    @property
    def es_docente(self):
        return ROL_DOCENTE in self.roles and not self.es_admin

    @property
    def es_estudiante(self):
        return ROL_ESTUDIANTE in self.roles and not self.es_admin

    @property
    def rol_principal(self):
        for r in (ROL_ADMIN, ROL_DOCENTE, ROL_ESTUDIANTE):
            if r in self.roles:
                return r
        return self.roles[0] if self.roles else "Sin rol"

    def tiene(self, permiso: str) -> bool:
        return permiso in self.permisos


def requerir(actor, permiso: str):
    """Lanza PermisoError si el usuario no tiene el permiso indicado."""
    if actor is None or not actor.tiene(permiso):
        raise PermisoError("No tiene permiso para realizar esta operación.")


def requerir_autenticado(actor):
    if actor is None:
        raise PermisoError("Debe iniciar sesión para realizar esta operación.")
