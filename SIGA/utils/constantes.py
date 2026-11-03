"""Constantes del sistema: roles, permisos, estados y datos iniciales."""
ROL_ADMIN = "Administrador"
ROL_DOCENTE = "Docente"
ROL_ESTUDIANTE = "Estudiante"

PRESENTE, AUSENTE, TARDANZA = "presente", "ausente", "tardanza"
ESTADOS_ASISTENCIA = (PRESENTE, AUSENTE, TARDANZA)
PENDIENTE, APROBADA, RECHAZADA = "pendiente", "aprobada", "rechazada"
ESTADOS_JUSTIFICACION = (PENDIENTE, APROBADA, RECHAZADA)
ESTADOS_MATRICULA = ("activa", "retirada", "finalizada")

DIAS_SEMANA = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves",
               5: "Viernes", 6: "Sábado", 7: "Domingo"}
SEXOS = {"M": "Masculino", "F": "Femenino"}
NIVELES_ACADEMICOS = ("Bachiller", "Técnico Medio", "Técnico Superior",
                      "Licenciatura", "Ingeniería", "Maestría", "Doctorado")

PERMISOS = {
    "usuarios.gestionar": "Crear usuarios, asignar roles y activar/desactivar cuentas",
    "estudiantes.gestionar": "Administrar estudiantes",
    "profesores.gestionar": "Administrar profesores",
    "catalogos.gestionar": "Administrar centros y catálogos académicos",
    "matriculas.gestionar": "Administrar matrículas",
    "asignaciones.gestionar": "Administrar asignaciones docentes",
    "asignaciones.consultar": "Consultar asignaciones y horario propios",
    "asistencia.registrar": "Registrar asistencia",
    "asistencia.consultar": "Consultar asistencia",
    "justificaciones.registrar": "Registrar justificaciones",
    "justificaciones.revisar": "Aprobar o rechazar justificaciones",
    "justificaciones.consultar": "Consultar justificaciones",
    "reportes.generar": "Generar reportes",
    "auditoria.consultar": "Consultar la auditoría",
    "respaldos.gestionar": "Crear respaldos de la base de datos",
}
PERMISOS_POR_ROL = {
    ROL_ADMIN: list(PERMISOS.keys()),
    ROL_DOCENTE: ["asignaciones.consultar", "asistencia.registrar", "asistencia.consultar",
                  "justificaciones.registrar", "justificaciones.revisar",
                  "justificaciones.consultar", "reportes.generar"],
    ROL_ESTUDIANTE: ["asignaciones.consultar", "asistencia.consultar",
                     "justificaciones.consultar"],
}

GRADOS_INICIALES = ["Séptimo", "Octavo", "Noveno", "Décimo", "Undécimo"]
SECCIONES_INICIALES = ["A", "B", "C"]
MODALIDADES_INICIALES = ["Regular", "Secundaria a Distancia en el Campo", "Jóvenes y Adultos"]
TURNOS_INICIALES = ["Matutino", "Vespertino", "Nocturno", "Sabatino"]
PERIODOS_INICIALES = [("Periodo 1", "07:00", "07:45"), ("Periodo 2", "07:45", "08:30"),
                      ("Periodo 3", "08:30", "09:15"), ("Periodo 4", "09:30", "10:15"),
                      ("Periodo 5", "10:15", "11:00"), ("Periodo 6", "11:00", "11:45"),
                      ("Periodo 7", "11:45", "12:30")]
