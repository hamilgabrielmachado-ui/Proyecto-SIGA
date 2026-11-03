# Migraciones

`database/init_db.py` usa `create_all()` solo para la **primera instalación** (crea tablas que faltan).
Cuando necesite cambiar tablas ya creadas (agregar columnas, etc.) use **Alembic**:

```
pip install alembic
alembic init database/migrations_alembic
```
Configure `sqlalchemy.url` leyendo `config.settings.get_database_url()` y `target_metadata = Base.metadata`
(importando `models`), luego use `alembic revision --autogenerate -m "descripcion"` y `alembic upgrade head`.
