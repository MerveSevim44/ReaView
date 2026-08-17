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

# Run migrations and table initialization on startup
def init_db():
    """Initialize database tables and run migrations safely"""
    try:
        from sqlalchemy import text
        from pathlib import Path
        import glob
        
        # 1. Create tables from SQLAlchemy models if they don't exist
        try:
            from . import models
            Base.metadata.create_all(bind=engine)
            print("[OK] Base.metadata.create_all completed")
        except Exception as e:
            print(f"[WARNING] Base.metadata.create_all warning: {e}")

        # 2. Run SQL migrations with per-statement transaction isolation
        migrations_path = Path(__file__).resolve().parent.parent / "migrations"
        migration_files = sorted(glob.glob(str(migrations_path / "*.sql")))
        
        if migration_files:
            for migration_file in migration_files:
                filename = Path(migration_file).name
                try:
                    with open(migration_file, encoding="utf-8") as f:
                        sql_content = f.read()
                        
                    lines = []
                    for line in sql_content.split('\n'):
                        if '--' in line:
                            line = line[:line.index('--')]
                        line = line.strip()
                        if line:
                            lines.append(line)
                    
                    sql_commands = ' '.join(lines)
                    for statement in sql_commands.split(';'):
                        statement = statement.strip()
                        # Ignore transaction-control keywords since engine.begin handles transactions
                        if not statement or statement.upper() in ["BEGIN", "COMMIT", "ROLLBACK", "END"]:
                            continue
                        if len(statement) > 3:
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text(statement))
                            except Exception as e:
                                error_msg = str(e).lower()
                                if not any(x in error_msg for x in [
                                    "already exists", 
                                    "duplicate", 
                                    "does not exist", 
                                    "undefined",
                                    "relation",
                                    "infailedsqltransaction",
                                    "empty query"
                                ]):
                                    print(f"[WARNING] Migration {filename} warning: {e}")
                    print(f"[OK] Migration {filename} processed")
                except Exception as e:
                    print(f"[ERROR] Error processing migration file {migration_file}: {e}")

        # 3. Explicit schema auto-healing for list privacy and critical columns
        auto_healing_statements = [
            "ALTER TABLE lists ADD COLUMN IF NOT EXISTS name VARCHAR(255) NOT NULL DEFAULT 'Untitled'",
            "ALTER TABLE lists ADD COLUMN IF NOT EXISTS description TEXT",
            "ALTER TABLE lists ADD COLUMN IF NOT EXISTS is_public INTEGER DEFAULT 0",
            "ALTER TABLE lists ADD COLUMN IF NOT EXISTS privacy_level INTEGER DEFAULT 0",
            "ALTER TABLE lists ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE lists ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE lists_item ADD COLUMN IF NOT EXISTS source_id VARCHAR(100)",
            "ALTER TABLE lists_item ADD COLUMN IF NOT EXISTS position INTEGER DEFAULT 0",
            "ALTER TABLE lists_item ADD COLUMN IF NOT EXISTS added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS list_id INTEGER",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS related_user_id INTEGER",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS review_id INTEGER",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)",
            "ALTER TABLE items ADD COLUMN IF NOT EXISTS external_rating INTEGER DEFAULT 0",
            "ALTER TABLE reviews ADD COLUMN IF NOT EXISTS source_id VARCHAR(100)",
            "ALTER TABLE reviews ADD COLUMN IF NOT EXISTS rating INTEGER DEFAULT 10",
            "UPDATE lists SET privacy_level = 2 WHERE (privacy_level IS NULL OR privacy_level = 0) AND is_public = 1",
            "UPDATE lists SET is_public = 1 WHERE privacy_level = 2"
        ]
        
        for ddl in auto_healing_statements:
            try:
                with engine.begin() as conn:
                    conn.execute(text(ddl))
            except Exception:
                pass
                
        print("[OK] Database initialization and schema verification complete")
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
