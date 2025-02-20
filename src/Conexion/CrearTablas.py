from BaseDatos import engine
from Tablas import Base

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

print("✅ Tablas creadas exitosamente en MySQL")
