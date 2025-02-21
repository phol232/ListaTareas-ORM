from BaseDatos import engine
from Tablas import Base


Base.metadata.create_all(engine)

print("✅ Tablas creadas exitosamente en MySQL")
