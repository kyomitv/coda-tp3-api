import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]


def init_schema() -> None:
    """Create application tables once if they do not exist."""
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS predictions ("
                "id SERIAL PRIMARY KEY, "
                "features TEXT, "
                "predicted INTEGER"
                ")"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS datasets ("
                "id SERIAL PRIMARY KEY, "
                "name TEXT, "
                "path TEXT"
                ")"
            )
        )
    engine.dispose()


if __name__ == "__main__":
    init_schema()
    print("Database schema initialized.")
