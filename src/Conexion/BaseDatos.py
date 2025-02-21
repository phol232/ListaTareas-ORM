import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "mysql+pymysql://root:root123456@localhost:3309/GestionTareas"

# La conexión inicial para crear la BD ya no es necesaria aquí.
# La haremos UNA SOLA VEZ en un script aparte (ver más abajo).

try:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()

except Exception as e:
    print(f"❌ Error de conexión: {str(e)}")
    raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
