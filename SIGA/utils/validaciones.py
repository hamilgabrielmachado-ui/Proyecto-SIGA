"""Validaciones reutilizables, pensadas para datos reales de Nicaragua.

Todas lanzan ValidacionError con mensajes claros y devuelven el valor ya normalizado.
"""
import re
from datetime import date, datetime, time

from utils.excepciones import ValidacionError
from utils.nombres_nicaragua import FEMENINOS, MASCULINOS, normalizar

# ---------------------------------------------------------------- patrones
_LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
_RE_PALABRA = re.compile(rf"^[{_LETRAS}]{{2,25}}$")
_RE_SOLO_TEXTO = re.compile(rf"^[{_LETRAS}]+(?: [{_LETRAS}]+)*$")
_RE_TEXTO_NUMERO = re.compile(rf"^[{_LETRAS}0-9]+(?: [{_LETRAS}0-9]+)*$")
_RE_CODIGO = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
_RE_CEDULA = re.compile(r"^(\d{3})-(\d{2})(\d{2})(\d{2})-(\d{4})([A-Za-z])$")
_RE_CEDULA_FORMATO = re.compile(r"^\d{3}-\d{6}-\d{4}[A-Za-z]$")
_RE_TELEFONO = re.compile(r"^\d{8}$")
_RE_CORREO_LOCAL = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_RE_CORREO_DOMINIO = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+[a-z]{2,}$")
_RE_MINED = re.compile(r"^LE-(\d{3})-SEC-(\d{3})$")
_RE_DIRECCION = re.compile(rf"^[{_LETRAS}0-9][{_LETRAS}0-9 ,.#°/-]*$")
_RE_USUARIO = re.compile(r"^[A-Za-z0-9._-]{4,50}$")

# Edades razonables (años).
EDAD_MIN_CEDULA = 16        # la cédula de identidad se emite desde los 16 años
EDAD_MIN_ESTUDIANTE = 10
EDAD_MAX_ESTUDIANTE = 70
EDAD_MIN_PROFESOR = 18
EDAD_MAX_PROFESOR = 75


def _limpiar(valor) -> str:
    """Convierte a texto y colapsa espacios repetidos."""
    if valor is None:
        return ""
    return re.sub(r"\s+", " ", str(valor)).strip()


# ---------------------------------------------------------------- texto general
def texto_requerido(valor, etiqueta: str, maximo: int = 100) -> str:
    valor = _limpiar(valor)
    if not valor:
        raise ValidacionError(f"El campo «{etiqueta}» es obligatorio.")
    if len(valor) > maximo:
        raise ValidacionError(f"El campo «{etiqueta}» admite máximo {maximo} caracteres.")
    return valor


def texto_opcional(valor, etiqueta: str, maximo: int = 100):
    valor = _limpiar(valor)
    if not valor:
        return None
    if len(valor) > maximo:
        raise ValidacionError(f"El campo «{etiqueta}» admite máximo {maximo} caracteres.")
    return valor


def solo_texto(valor, etiqueta: str, requerido=True, minimo=3, maximo=150):
    """Solo letras (con tildes y ñ) y espacios."""
    v = texto_requerido(valor, etiqueta, maximo) if requerido else texto_opcional(valor, etiqueta, maximo)
    if v is None:
        return None
    if not _RE_SOLO_TEXTO.match(v):
        raise ValidacionError(f"«{etiqueta}» solo admite letras y espacios (sin números ni símbolos).")
    if len(v) < minimo:
        raise ValidacionError(f"«{etiqueta}» debe tener al menos {minimo} letras.")
    return v


def texto_con_numeros(valor, etiqueta: str, requerido=True, minimo=3, maximo=100):
    """Letras, números y espacios (por ejemplo «Periodo 1»)."""
    v = texto_requerido(valor, etiqueta, maximo) if requerido else texto_opcional(valor, etiqueta, maximo)
    if v is None:
        return None
    if not _RE_TEXTO_NUMERO.match(v):
        raise ValidacionError(f"«{etiqueta}» solo admite letras, números y espacios.")
    if len(v) < minimo:
        raise ValidacionError(f"«{etiqueta}» debe tener al menos {minimo} caracteres.")
    if not re.search(rf"[{_LETRAS}]", v):
        raise ValidacionError(f"«{etiqueta}» debe incluir letras.")
    return v


def validar_codigo_alfanumerico(valor, etiqueta: str, requerido=True, minimo=3, maximo=30):
    """Letras, números y guiones (sin espacios, sin guiones al inicio, al final ni repetidos)."""
    v = texto_requerido(valor, etiqueta, maximo) if requerido else texto_opcional(valor, etiqueta, maximo)
    if v is None:
        return None
    if not _RE_CODIGO.match(v):
        raise ValidacionError(f"«{etiqueta}» solo admite letras, números y guiones, sin espacios ni símbolos "
                              "(no puede iniciar ni terminar con guion ni tener guiones seguidos).")
    if len(v) < minimo:
        raise ValidacionError(f"«{etiqueta}» debe tener al menos {minimo} caracteres.")
    return v.upper()


def validar_direccion(valor, etiqueta="Dirección", requerido=False, minimo=5, maximo=200):
    """Texto de dirección: letras, números y signos básicos (, . # - / °). Típico: «Del parque 2 c. al sur»."""
    v = texto_requerido(valor, etiqueta, maximo) if requerido else texto_opcional(valor, etiqueta, maximo)
    if v is None:
        return None
    if not _RE_DIRECCION.match(v):
        raise ValidacionError(f"«{etiqueta}» solo admite letras, números y los signos , . # - / °")
    if len(re.findall(rf"[{_LETRAS}]", v)) < 3:
        raise ValidacionError(f"«{etiqueta}» debe describir el lugar con texto (al menos 3 letras).")
    if len(v) < minimo:
        raise ValidacionError(f"«{etiqueta}» debe tener al menos {minimo} caracteres.")
    return v


def validar_nombre_usuario(valor):
    v = texto_requerido(valor, "Usuario", 50)
    if not _RE_USUARIO.match(v):
        raise ValidacionError("El usuario debe tener de 4 a 50 caracteres: letras, números, punto, guion o "
                              "guion bajo, sin espacios.")
    return v


# ---------------------------------------------------------------- personas
def validar_nombre_persona(valor, etiqueta: str, cantidad=2):
    """Solo letras; exactamente `cantidad` palabras (dos nombres o dos apellidos). Se permiten repetidos."""
    v = texto_requerido(valor, etiqueta, 100)
    palabras = v.split(" ")
    if any(not _RE_PALABRA.match(p) for p in palabras):
        raise ValidacionError(f"«{etiqueta}» solo admite letras (mínimo 2 por palabra), sin números, "
                              "guiones ni símbolos.")
    if len(palabras) != cantidad:
        raise ValidacionError(f"«{etiqueta}» debe tener exactamente {cantidad} palabras "
                              f"(escribió {len(palabras)}).")
    return " ".join(p.capitalize() for p in palabras)


def validar_sexo_con_nombre(sexo: str, nombres: str):
    """No se acepta sexo femenino con nombre masculino ni masculino con nombre femenino."""
    primero = normalizar(nombres.split(" ")[0])
    if sexo == "F" and primero in MASCULINOS:
        raise ValidacionError(f"El nombre «{nombres.split(' ')[0]}» es masculino; no coincide con el sexo "
                              "Femenino. Corrija el sexo o el nombre.")
    if sexo == "M" and primero in FEMENINOS:
        raise ValidacionError(f"El nombre «{nombres.split(' ')[0]}» es femenino; no coincide con el sexo "
                              "Masculino. Corrija el sexo o el nombre.")


def validar_telefono(valor):
    """Teléfono nicaragüense: exactamente 8 dígitos y solo números (inicia en 2, 5, 7 u 8)."""
    v = texto_opcional(valor, "Teléfono", 20)
    if v is None:
        return None
    if not v.isdigit() or not v.isascii():
        raise ValidacionError("El teléfono solo admite números (sin espacios, guiones ni +505).")
    if not _RE_TELEFONO.match(v):
        raise ValidacionError("El teléfono debe tener exactamente 8 dígitos.")
    if v[0] not in "2578":
        raise ValidacionError("Un teléfono de Nicaragua inicia con 2 (convencional) o con 5, 7 u 8 (celular).")
    if len(set(v)) == 1:
        raise ValidacionError("El teléfono no es válido (todos los dígitos son iguales).")
    return v


def validar_correo(valor):
    """Estructura tipo mariorodriguezprofe@gmail.com. Se guarda en minúsculas."""
    v = texto_opcional(valor, "Correo", 120)
    if v is None:
        return None
    v = v.lower()
    if " " in v or v.count("@") != 1:
        raise ValidacionError("El correo electrónico debe tener la forma usuario@dominio.com (un solo @, "
                              "sin espacios).")
    local, dominio = v.split("@")
    if not local or len(local) > 64 or not _RE_CORREO_LOCAL.match(local):
        raise ValidacionError("La parte anterior al @ solo admite letras, números y . _ - (sin signos "
                              "al inicio, al final ni repetidos).")
    if not _RE_CORREO_DOMINIO.match(dominio):
        raise ValidacionError("El dominio del correo no es válido (ejemplo: gmail.com).")
    return v


# ---------------------------------------------------------------- cédula nicaragüense
def edad_en(fecha_nac: date, hoy: date = None) -> int:
    hoy = hoy or date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))


def validar_cedula(valor, requerida=False):
    """Formato XXX-DDMMYY-XXXXL: municipio (3), fecha de nacimiento (6), número (4) y letra verificadora."""
    v = texto_requerido(valor, "Cédula", 20) if requerida else texto_opcional(valor, "Cédula", 20)
    if v is None:
        return None
    v = v.upper()
    if not _RE_CEDULA_FORMATO.match(v):
        raise ValidacionError("La cédula debe tener el formato XXX-DDMMYY-XXXXL (3 dígitos del municipio, "
                              "fecha de nacimiento DDMMYY, 4 dígitos y una letra al final). "
                              "Ejemplo: 001-150695-0001A.")
    municipio, dd, mm, aa, numero, _ = _RE_CEDULA.match(v).groups()
    if municipio == "000":
        raise ValidacionError("El código de municipio de la cédula (primeros 3 dígitos) no es válido.")
    if numero == "0000":
        raise ValidacionError("El número de persona de la cédula (4 dígitos) no puede ser 0000.")
    nacimiento = fecha_de_cedula(v)
    if nacimiento is None:
        raise ValidacionError(f"La fecha de nacimiento dentro de la cédula ({dd}/{mm}/{aa}) no es una "
                              "fecha real o está en el futuro.")
    if edad_en(nacimiento) < EDAD_MIN_CEDULA:
        raise ValidacionError(f"La cédula indica una persona menor de {EDAD_MIN_CEDULA} años; la cédula se "
                              "emite a partir de esa edad.")
    return v


def fecha_de_cedula(cedula: str):
    """Fecha de nacimiento codificada en la cédula, o None si no es una fecha real.

    Como solo hay 2 dígitos de año, se elige el siglo más reciente que no sea futuro ni dé más de 100 años.
    """
    m = _RE_CEDULA.match(cedula or "")
    if not m:
        return None
    dd, mm, aa = int(m.group(2)), int(m.group(3)), int(m.group(4))
    hoy = date.today()
    for anio in (2000 + aa, 1900 + aa):
        try:
            f = date(anio, mm, dd)
        except ValueError:
            continue
        if f <= hoy and edad_en(f) <= 100:
            return f
    return None


def validar_cedula_con_fecha(cedula, fecha_nacimiento):
    """La fecha que contiene la cédula debe coincidir con la fecha de nacimiento registrada."""
    if not cedula or not fecha_nacimiento:
        return
    f = fecha_de_cedula(cedula)
    if f and (f.day, f.month, f.year % 100) != (fecha_nacimiento.day, fecha_nacimiento.month,
                                                fecha_nacimiento.year % 100):
        raise ValidacionError("La fecha de nacimiento no coincide con la fecha que contiene la cédula "
                              f"({f:%d/%m/%Y}).")


# ---------------------------------------------------------------- fechas y números
def validar_fecha_pasada(valor, etiqueta="Fecha"):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        valor = valor.date()
    if not isinstance(valor, date):
        raise ValidacionError(f"«{etiqueta}» no es una fecha válida.")
    if valor > date.today():
        raise ValidacionError(f"«{etiqueta}» no puede ser una fecha futura.")
    return valor


def validar_fecha_nacimiento(valor, etiqueta, edad_min, edad_max):
    f = validar_fecha_pasada(valor, etiqueta)
    if f is None:
        return None
    edad = edad_en(f)
    if edad < edad_min:
        raise ValidacionError(f"«{etiqueta}»: la edad ({edad} años) es menor que la mínima permitida ({edad_min}).")
    if edad > edad_max:
        raise ValidacionError(f"«{etiqueta}»: la edad ({edad} años) supera el máximo permitido ({edad_max}).")
    return f


def parsear_hora(valor, etiqueta="Hora") -> time:
    if isinstance(valor, time):
        return valor
    try:
        return datetime.strptime(str(valor).strip(), "%H:%M").time()
    except ValueError:
        raise ValidacionError(f"«{etiqueta}» debe tener el formato HH:MM (por ejemplo 07:30).")


def entero_en_rango(valor, etiqueta, minimo, maximo, requerido=False):
    if valor in (None, ""):
        if requerido:
            raise ValidacionError(f"El campo «{etiqueta}» es obligatorio.")
        return None
    try:
        n = int(valor)
    except (TypeError, ValueError):
        raise ValidacionError(f"«{etiqueta}» debe ser un número entero.")
    if not minimo <= n <= maximo:
        raise ValidacionError(f"«{etiqueta}» debe estar entre {minimo} y {maximo}.")
    return n


# ---------------------------------------------------------------- profesores
def validar_codigo_mined(valor):
    """Estructura única: LE-001-SEC-001."""
    v = texto_requerido(valor, "Código MINED", 30).upper()
    m = _RE_MINED.match(v)
    if not m:
        raise ValidacionError("El código MINED debe tener exactamente la estructura LE-001-SEC-001 "
                              "(LE-###-SEC-###).")
    if m.group(1) == "000" or m.group(2) == "000":
        raise ValidacionError("Los números del código MINED no pueden ser 000.")
    return v


def validar_especialidad(valor):
    """Solo palabras y, como máximo, un número (por ejemplo «Matemática» o «Informática 2»)."""
    v = texto_opcional(valor, "Especialidad", 100)
    if v is None:
        return None
    if not _RE_TEXTO_NUMERO.match(v):
        raise ValidacionError("La especialidad solo admite palabras y un número (sin símbolos).")
    palabras = v.split(" ")
    numeros = [p for p in palabras if p.isdigit()]
    if any(not p.isdigit() and re.search(r"\d", p) for p in palabras):
        raise ValidacionError("La especialidad no puede mezclar letras y números en una misma palabra.")
    if len(numeros) > 1:
        raise ValidacionError("La especialidad admite un solo número.")
    if numeros and len(numeros[0]) > 2:
        raise ValidacionError("El número de la especialidad admite máximo 2 dígitos.")
    if len(palabras) == len(numeros):
        raise ValidacionError("La especialidad debe incluir al menos una palabra.")
    if any(len(p) < 2 for p in palabras if not p.isdigit()) and len(palabras) == 1:
        raise ValidacionError("La especialidad debe tener al menos 2 letras.")
    return v
