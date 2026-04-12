"""
SortMail Configuration
----------------------
All environment variables and settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    VERSION: str = "0.1.0-beta"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False  # SECURITY: Disabled by default in production
    DISABLE_API_DOCS_IN_PRODUCTION: bool = True
    INTERNAL_SERVICE_TOKEN: str = ""
    
    # Server
    # CORS
    # STRICT PRODUCTION SECURITY: Only allow the actual frontend domain.
    # Localhost is removed to prevent local unauthorized clients from browser-side calls.
    CORS_ORIGINS: List[str] = [
        "https://sortmail.vercel.app", 
        # Add "http://localhost:3000" here manually if developing locally
    ]
    
    # Frontend URL (for redirects)
    FRONTEND_URL: str # Required in production
    
    # Database
    DATABASE_URL: str # Required
    
    # Redis (optional for MVP, required for Prod)
    REDIS_URL: str # Required
    
    # OAuth - Google
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str # Required
    
    # Google Cloud Pub/Sub
    GOOGLE_PUBSUB_TOPIC_NAME: str = "" # Expected format: projects/{project}/topics/{topic}
    
    # OAuth - Microsoft
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_REDIRECT_URI: str # Required
    
    # JWT
    JWT_SECRET: str # Required
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # LLM: Bedrock Nova for intelligence, Gemini/OpenAI for embeddings if needed
    LLM_PROVIDER: str = "gemini"  # "gemini" | "openai" — used for embeddings only
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    HF_TOKEN: str = ""
    BEDROCK_REGION_NAME: str = ""
    BEDROCK_MODEL_ID: str = "us.amazon.nova-2-lite-v1:0"
    INTEL_TWO_PASS_ENABLED: bool = True
    INTEL_PASS1_MODEL_ID: str = "amazon.nova-micro-v1:0"
    INTEL_PASS2_MODEL_ID: str = "us.amazon.nova-2-lite-v1:0"
    AI_AUTODRAFT_ENABLED: bool = False
    EMBEDDING_PROVIDER: str = "bedrock"  # "bedrock" | "gemini" | "openai"
    BEDROCK_EMBED_MODEL_ID: str = "amazon.titan-embed-text-v2:0"
    BEDROCK_EMBED_DIMENSIONS: int = 1024
    BEDROCK_EMBED_NORMALIZE: bool = True
    EMBEDDING_PROVIDER_INPUT_PER_MILLION_USD: float = 0.02
    EMBEDDING_USER_INPUT_PER_MILLION_USD: float = 0.08
    
    # Chroma Cloud
    CHROMA_HOST: str = "api.trychroma.com"
    CHROMA_API_KEY: str = ""
    CHROMA_TENANT: str = ""
    CHROMA_DATABASE: str = ""
    CHROMA_COLLECTION_NAME: str = "my_collection"
    
    # S3 Storage (Tier 3 Cold Storage)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION_NAME: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    S3_ENDPOINT_URL: str = "" # Supported for Cloudflare R2 compatibility
    
    # Security
    ENCRYPTION_KEY: str = "" # Required in production (32-byte base64)
    
    # Vector DB
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # File Storage
    STORAGE_PATH: str = "./data/attachments"
    MAX_ATTACHMENT_SIZE_MB: int = 25
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
