from app.config import BASE_DIR

DB_FILE = BASE_DIR / "app.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"
