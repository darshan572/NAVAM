from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

db_url = settings.database_url
# For sync create_engine, ensure driver is standard postgresql://
if "+asyncpg" in db_url:
    db_url = db_url.replace("+asyncpg", "")
if "sslmode=require" not in db_url and "neon.tech" in db_url:
    if "ssl=require" in db_url:
        db_url = db_url.replace("ssl=require", "sslmode=require")
    else:
        sep = "&" if "?" in db_url else "?"
        db_url += f"{sep}sslmode=require"

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
