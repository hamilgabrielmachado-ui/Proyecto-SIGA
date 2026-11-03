class BaseRepository:
    """Operaciones comunes. Los repositorios reciben una sesión ya abierta."""
    modelo = None

    def __init__(self, session):
        self.s = session

    def obtener(self, id_):
        return self.s.get(self.modelo, id_)

    def agregar(self, obj):
        self.s.add(obj)
        self.s.flush()
        return obj

    def eliminar(self, obj):
        self.s.delete(obj)
        self.s.flush()
