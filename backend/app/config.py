"""
Configuration management for ShootSafe AI backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database (SQLite - no setup needed!)
    database_url: str = "sqlite+aiosqlite:///./shootsafe.db"
    sync_database_url: str = "sqlite:///./shootsafe.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    # LLM (Gemini)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    gemini_request_delay: float = 1.2
    
    # RAG / Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "shootsafe_knowledge"
    
    # Storage
    storage_path: str = "./storage"
    upload_max_size_mb: int = 100
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Features
    paraphrase_enabled: bool = True
    extract_self_consistency: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
