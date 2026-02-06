"""
Configuration management for SME Financial Platform
Loads settings from environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "SME Financial Health Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password@localhost:5432/sme_financial_db")
    DB_ECHO: bool = False  # Set to True to log SQL queries
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Encryption (AES-256)
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # AI Services
    AI_PROVIDER: str = "gemini"  # "openai", "claude", "openrouter", or "gemini"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-opus-20240229"
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = "google/gemini-pro"
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Banking Integration
    PLAID_CLIENT_ID: Optional[str] = None
    PLAID_SECRET: Optional[str] = None
    PLAID_ENV: str = "sandbox"  # sandbox, development, or production
    
    # Payment Integration
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    
    # GST Integration
    GST_API_URL: str = "https://api.gst.gov.in"
    GST_CLIENT_ID: Optional[str] = None
    GST_CLIENT_SECRET: Optional[str] = None
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = ['.csv', '.xlsx', '.xls', '.pdf']
    UPLOAD_DIR: str = "./uploads"
    
    # Multilingual
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: list = ["en", "hi"]
    
    # Industry Categories
    INDUSTRIES: list = [
        "Manufacturing",
        "Retail",
        "Agriculture",
        "Services",
        "Logistics",
        "E-commerce",
        "Healthcare",
        "Education",
        "Hospitality",
        "Construction",
        "IT & Software",
        "Other"
    ]
    
    # Credit Scoring
    CREDIT_SCORE_MIN: int = 300
    CREDIT_SCORE_MAX: int = 900
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Ensure required directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        settings.UPLOAD_DIR,
        os.path.dirname(settings.LOG_FILE),
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


ensure_directories()
