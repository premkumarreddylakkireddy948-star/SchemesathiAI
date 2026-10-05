import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SchemeSathi AI"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "production"  # "development" or "production"
    
    # Environment Variables
    LLM_API_KEY: str = "gemini_production_key_active"
    GEMINI_API_KEY: str = "gemini_production_key_active"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/schemesathi"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    JWT_SECRET: str = "schemesathi_secret_jwt_key_2026_super_secure"
    FRONTEND_URL: str = "https://temporary-prompt-indigo-zwrnvfm.vercel.app"
    CORS_ORIGINS: str = "*,http://localhost:3000,http://127.0.0.1:3000,https://temporary-prompt-indigo-zwrnvfm.vercel.app"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ["production", "prod"]

    @property
    def effective_llm_key(self) -> str:
        return self.GEMINI_API_KEY or self.LLM_API_KEY or os.getenv("GEMINI_API_KEY", "") or os.getenv("LLM_API_KEY", "") or "active_production_key"

    @property
    def parsed_cors_origins(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return ["*"] if not self.is_production else [self.FRONTEND_URL]
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
