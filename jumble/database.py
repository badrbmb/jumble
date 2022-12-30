import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

DB_URL = os.environ.get("POSTGRES_DATABASE_URL")
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == "__main__":

    # create database if not exist
    if not database_exists(engine.url):
        print(f"Creating DB: {engine.url}")
        create_database(engine.url)

    print(engine.url)

    with SessionLocal() as db:
        print(
            db.execute(
                """
            SELECT * FROM information_schema.tables
            WHERE table_schema = 'public'
            """
            ).fetchall()
        )
