"""Reglas de identidad compartidas entre estudiantes y profesores."""
from sqlalchemy import select

from models import Estudiante, Profesor
from utils.excepciones import DuplicadoError


def verificar_cedula_unica(s, cedula, id_estudiante=None, id_profesor=None):
    """Una cédula identifica a una sola persona: no puede repetirse entre estudiantes ni profesores."""
    if not cedula:
        return
    est = s.scalar(select(Estudiante).where(Estudiante.cedula == cedula))
    if est and est.id_estudiante != id_estudiante:
        raise DuplicadoError("Esa cédula ya está registrada para otro estudiante.")
    prof = s.scalar(select(Profesor).where(Profesor.cedula == cedula))
    if prof and prof.id_profesor != id_profesor:
        raise DuplicadoError("Esa cédula ya está registrada para otro profesor.")
