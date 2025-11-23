from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path
import warnings


# Try to load .env from working dir first, then from the package folder.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    package_env = Path(__file__).resolve().parent / ".env"
    if package_env.exists():
        load_dotenv(package_env)
        DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Provide a safe fallback for local development so create_engine doesn't
    # receive None. In production you should set DATABASE_URL to your
    # PostgreSQL (or other) DSN. We default to a local SQLite file.
    warnings.warn(
        "DATABASE_URL not set. Falling back to a local SQLite database at './dev.db'. "
        "Set the DATABASE_URL environment variable or create a backend/app/.env file to configure a real DB.",
        RuntimeWarning,
    )
    DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parent.parent / 'dev.db'}"

# Create the engine (will raise for invalid URLs)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Run migrations on startup
def init_db():
    """Initialize database with migrations"""
    try:
        from sqlalchemy import text
        from pathlib import Path
        import glob
        
        migrations_path = Path(__file__).resolve().parent.parent / "migrations"
        
        # Get all migration files sorted by name
        migration_files = sorted(glob.glob(str(migrations_path / "*.sql")))
        
        if not migration_files:
            print("[INFO] No migration files found")
            return
        
        with engine.connect() as conn:
            for migration_file in migration_files:
                try:
                    with open(migration_file) as f:
                        sql_content = f.read()
                        filename = Path(migration_file).name
                        
                        # Remove comments and split by semicolon
                        lines = []
                        for line in sql_content.split('\n'):
                            # Remove SQL comments
                            if '--' in line:
                                line = line[:line.index('--')]
                            line = line.strip()
                            if line:
                                lines.append(line)
                        
                        sql_commands = ' '.join(lines)
                        
                        # Execute each SQL statement
                        for statement in sql_commands.split(';'):
                            statement = statement.strip()
                            if statement and len(statement) > 5:  # Ignore very short statements
                                try:
                                    conn.execute(text(statement))
                                except Exception as e:
                                    error_msg = str(e)
                                    # Ignore certain expected errors
                                    if not any(x in error_msg for x in ["already exists", "does not exist", "InFailedSqlTransaction", "empty query"]):
                                        print(f"[WARNING] Migration {filename} warning: {e}")
                        conn.commit()
                        print(f"[OK] Migration {filename} completed")
                except Exception as e:
                    print(f"[ERROR] Error reading migration file {migration_file}: {e}")
    except Exception as e:
        print(f"[ERROR] Database init error: {e}")


# Dependency (route içinde kullanmak için)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import models after Base and SessionLocal are defined to avoid circular imports
from . import models
