class SigaError(Exception):
    """Error controlado: su mensaje es apto para mostrarse al usuario."""

class ValidacionError(SigaError): pass
class DuplicadoError(SigaError): pass
class PermisoError(SigaError): pass
class NoEncontradoError(SigaError): pass
class AutenticacionError(SigaError): pass
