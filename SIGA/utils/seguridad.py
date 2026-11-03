"""Hash de contraseñas con bcrypt y reglas de contraseña."""
import secrets
import string

import bcrypt

from utils.excepciones import ValidacionError


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hash_guardado.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def validar_fortaleza(password: str) -> None:
    if not password or len(password) < 8:
        raise ValidacionError("La contraseña debe tener al menos 8 caracteres.")
    if len(password.encode("utf-8")) > 72:
        raise ValidacionError("La contraseña es demasiado larga (máximo 72 caracteres).")
    if any(c.isspace() for c in password):
        raise ValidacionError("La contraseña no puede contener espacios.")
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise ValidacionError("La contraseña debe combinar letras y números.")


def generar_password_temporal(largo: int = 10) -> str:
    alfabeto = string.ascii_letters + string.digits
    while True:
        clave = "".join(secrets.choice(alfabeto) for _ in range(largo))
        if any(c.isalpha() for c in clave) and any(c.isdigit() for c in clave):
            return clave
