from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_PATH = Path("data/app.db")

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine)