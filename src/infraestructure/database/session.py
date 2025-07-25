from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import NullPool
from src.infraestructure.config.settings import settings

Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL, echo=False, future=True, poolclass=NullPool
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
