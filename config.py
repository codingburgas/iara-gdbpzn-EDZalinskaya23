"""Application settings."""
import os

# Project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Secret key for sessions (use an environment variable in production)
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

    # SQLite database file
    DATABASE = os.path.join(BASE_DIR, "database", "gdpbzn.db")

    # SQL files used to create and seed the database
    SCHEMA_SQL = os.path.join(BASE_DIR, "database", "schema.sql")
    SEED_SQL = os.path.join(BASE_DIR, "database", "seed.sql")
