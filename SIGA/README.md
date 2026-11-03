# SIGA — Sistema Integral de Gestión de Asistencia Escolar

Aplicación de escritorio en **Python + PySide6 + SQLAlchemy + MySQL**.

## 1. Instalación (Windows / VS Code)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Base de datos MySQL
En MySQL Workbench o consola:
```sql
CREATE DATABASE siga_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Copie `.env.example` como `.env` y complete `DB_USER`, `DB_PASSWORD` y `DB_NAME`.
**Nunca** suba `.env` al repositorio (ya está en `.gitignore`).

## 3. Ejecutar
```
python main.py
```
La primera vez se crean las tablas, roles, permisos y catálogos iniciales (grados 7°–11°, secciones A–C,
modalidades, turnos, periodos y año lectivo actual) y el administrador inicial. Si `ADMIN_PASSWORD` está
vacío en `.env`, se muestra **una sola vez** una contraseña temporal; el sistema pedirá cambiarla.

### Datos de demostración (opcional)
```
python -m database.seed_demo
```
Crea un docente (`docente` / `Demo1234`), un estudiante (`estudiante` / `Demo1234`), un grupo con 6 estudiantes
y clases de lunes a viernes. Úselo solo para probar.

### Orden recomendado de configuración (administrador)
1. Centros y catálogos (centro, asignaturas; revise periodos y año lectivo).
2. Estudiantes y profesores.
3. Matrículas y asignaciones (cada asignación incluye día y periodo).
4. Usuarios: cree cuentas vinculadas a profesores/estudiantes.

## 4. Pruebas
```
python -m pytest -q
```
Las pruebas usan SQLite temporal; no tocan su MySQL.

## 5. Arquitectura
`views` (interfaz) → `controllers` (mensajes y errores) → `services` (reglas y **permisos**) →
`repositories` (consultas) → `models` (SQLAlchemy). Estilos en `resources/styles/*.qss`.
Los permisos se verifican en cada servicio; ocultar menús es solo comodidad.

## 6. Decisiones y notas
- Estudiante: código estudiantil único (obligatorio) y cédula opcional única.
- Docente y estudiante inician sesión con su **nombre de usuario**.
- Se agregó el **día de la semana** a las asignaciones (necesario para los horarios).
- % de asistencia = (presentes + tardanzas) / total de registros.
- Contraseñas con bcrypt; bloqueo de 5 minutos tras 5 intentos fallidos.
- Respaldos: requieren `mysqldump` en el PATH.
- `create_all()` solo crea tablas faltantes; para cambios de esquema use Alembic (ver `database/migrations/README.md`).
- Dependencias agregadas respecto al prompt: bcrypt, reportlab, openpyxl.
