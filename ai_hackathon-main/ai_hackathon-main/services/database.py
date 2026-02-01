import os
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

# SQLAlchemy imports for Postgres
try:
    from sqlalchemy import create_engine, Column, String, JSON, DateTime, Integer
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

Base = declarative_base() if SQLALCHEMY_AVAILABLE else object

# Define Model for Postgres
if SQLALCHEMY_AVAILABLE:
    class MetadataModel(Base):
        __tablename__ = 'metadata'
        file_hash = Column(String, primary_key=True)
        data = Column(JSON)
        created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseService(ABC):
    @abstractmethod
    def save_metadata(self, file_hash: str, metadata: Dict[str, Any]):
        """Saves metadata associated with a file hash."""
        pass

    @abstractmethod
    def get_metadata(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata by file hash."""
        pass

class JsonFileDB(DatabaseService):
    def __init__(self, cache_dir: str = "outputs/cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def save_metadata(self, file_hash: str, metadata: Dict[str, Any]):
        path = os.path.join(self.cache_dir, f"{file_hash}.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
        except Exception as e:
            print(f"Failed to save JSON cache: {e}")

    def get_metadata(self, file_hash: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(self.cache_dir, f"{file_hash}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                         data["_db_source"] = "local_json"
                    return data
            except Exception:
                return None
        return None

class PostgresDB(DatabaseService):
    def __init__(self, connection_string: str):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is not installed. Please install it to use PostgresDB.")
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine) # Ensure table exists
        self.Session = sessionmaker(bind=self.engine)

    def save_metadata(self, file_hash: str, metadata: Dict[str, Any]):
        session = self.Session()
        try:
            # Check if exists, update or insert
            existing = session.query(MetadataModel).filter_by(file_hash=file_hash).first()
            if existing:
                existing.data = metadata
                existing.created_at = datetime.utcnow()
            else:
                new_record = MetadataModel(file_hash=file_hash, data=metadata)
                session.add(new_record)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Postgres Error: {e}")
            raise e
        finally:
            session.close()

    def get_metadata(self, file_hash: str) -> Optional[Dict[str, Any]]:
        session = self.Session()
        try:
            record = session.query(MetadataModel).filter_by(file_hash=file_hash).first()
            if record:
                data = record.data
                if isinstance(data, dict):
                    data["_db_source"] = "postgres"
                return data
            return None
        finally:
            session.close()

def get_db_service() -> DatabaseService:
    """Factory to get DB service."""
    # Check if a DATABASE_URL is provided (Standard pattern for Render/Heroku Postgres)
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        if not SQLALCHEMY_AVAILABLE:
            print("DATABASE_URL found but SQLAlchemy missing. Using JSON DB.")
            return JsonFileDB()
        print("Using PostgreSQL Database")
        return PostgresDB(db_url)
    
    print("Using Local JSON Database")
    return JsonFileDB()
