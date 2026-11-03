"""Datos de demostración opcionales: python -m database.seed_demo"""
from sqlalchemy import select

from database.init_db import inicializar
from database.connection import get_session
from models import (AnioLectivo, AsignacionDocente, Asignatura, CentroEducativo, Estudiante, Grado, Matricula,
                    Modalidad, PeriodoClase, Profesor, Seccion, Turno, Usuario, Rol)
from utils.seguridad import hash_password

CLAVE = "Demo1234"


def sembrar():
    inicializar()
    with get_session() as s:
        if s.scalar(select(Profesor).where(Profesor.cedula == "001-150685-0001A")):
            return False
        centro = CentroEducativo(nombre="Instituto Demo", codigo="C-001", direccion="Del parque central 2 cuadras al sur, Managua")
        mat, leng = Asignatura(nombre="Matemática"), Asignatura(nombre="Lengua y Literatura")
        s.add_all([centro, mat, leng]); s.flush()
        anio = s.scalar(select(AnioLectivo).order_by(AnioLectivo.anio.desc()))
        grado = s.scalar(select(Grado).where(Grado.nombre == "Séptimo"))
        sec = s.scalar(select(Seccion).where(Seccion.nombre == "A"))
        mod = s.scalar(select(Modalidad).where(Modalidad.nombre == "Regular"))
        turno = s.scalar(select(Turno).where(Turno.nombre == "Matutino"))
        per = s.scalars(select(PeriodoClase).order_by(PeriodoClase.hora_inicio)).all()
        prof = Profesor(nombres="Marta Elena", apellidos="López Ruiz", cedula="001-150685-0001A", codigo_mined="LE-001-SEC-001",
                        especialidad="Matemática", nivel_academico="Licenciatura", id_centro=centro.id_centro,
                        id_turno=turno.id_turno, anios_experiencia=8)
        s.add(prof); s.flush()
        for dia in range(1, 6):
            s.add(AsignacionDocente(id_profesor=prof.id_profesor, id_centro=centro.id_centro, id_anio=anio.id_anio,
                                    id_grado=grado.id_grado, id_seccion=sec.id_seccion, id_asignatura=mat.id_asignatura,
                                    id_periodo=per[0].id_periodo, id_modalidad=mod.id_modalidad, dia_semana=dia))
        nombres = [("Ana María", "Pérez Gómez"), ("Luis Carlos", "Gómez Rivas"), ("Sofía Isabel", "Martínez Díaz"),
                ("Carlos Andrés", "Rivas Mejía"), ("Elena Patricia", "Torres Solís"),
                ("Diego Alejandro", "Castillo Pérez")]
        for i, (n, a) in enumerate(nombres, 1):
            e = Estudiante(codigo=f"E-{i:03d}", nombres=n, apellidos=a, sexo="F" if n.split()[0] in ("Ana", "Sofía", "Elena") else "M")
            s.add(e); s.flush()
            s.add(Matricula(id_estudiante=e.id_estudiante, id_anio=anio.id_anio, id_centro=centro.id_centro,
                            id_grado=grado.id_grado, id_seccion=sec.id_seccion, estado="activa"))
            if i == 1:
                u = Usuario(username="estudiante", password_hash=hash_password(CLAVE), id_estudiante=e.id_estudiante)
                u.roles.append(s.scalar(select(Rol).where(Rol.nombre == "Estudiante"))); s.add(u)
        u = Usuario(username="docente", password_hash=hash_password(CLAVE), id_profesor=prof.id_profesor)
        u.roles.append(s.scalar(select(Rol).where(Rol.nombre == "Docente"))); s.add(u)
    return True


if __name__ == "__main__":
    if sembrar():
        print(f"Datos de demostración creados.\n  docente / {CLAVE}\n  estudiante / {CLAVE}")
    else:
        print("Los datos de demostración ya existían.")
