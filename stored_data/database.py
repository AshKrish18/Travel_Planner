from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://postgres:secret_password@localhost:5432/travel_db"

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass


session_local = sessionmaker(bind = engine)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
