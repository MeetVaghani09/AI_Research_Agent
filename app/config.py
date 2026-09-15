
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DOCUMENTS_DIR = DATA_DIR / "documents"


# ---------------------------------------------------------
# Application settings
# ---------------------------------------------------------

class Settings(BaseSettings):
    # Application
    app_name: str = "AI Research Agent"
    app_version: str = "3.0.0"
    environment: str = "development"

    # LLM
    deepseek_api_key: str
    deepseek_model: str = "deepseek-v4-flash"

    # Web search
    tavily_api_key: str | None = None

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "research_documents"

    # Redis
    redis_url: str | None = None
    default_session_id: str = "research-user"

    # LangSmith
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "ai-research-agent"
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    # File upload
    max_upload_size_mb: int = Field(default=25, ge=1, le=500)

    # RAG
    retrieval_top_k: int = Field(default=5, ge=1, le=50)

    # CORS
    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def max_upload_size_bytes(self) -> int:
        """Maximum allowed upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        """Convert comma-separated CORS origins into a list."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


# ---------------------------------------------------------
# Global settings instance
# ---------------------------------------------------------

settings = Settings()

