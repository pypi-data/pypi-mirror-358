"""Configuration management for LLMomics."""

from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Config(BaseSettings):
    """Global configuration for LLMomics."""

    # LLM Configuration
    llm_provider: str = Field(default="openai", description="LLM provider to use")
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(
        default="gpt-3.5-turbo", description="OpenAI model to use"
    )

    # Data Sources Configuration
    ncbi_api_key: Optional[str] = Field(
        default=None, json_schema_extra={"env": "NCBI_API_KEY"}
    )
    ncbi_email: Optional[str] = Field(
        default=None, json_schema_extra={"env": "NCBI_EMAIL"}
    )

    # Pipeline Configuration
    output_dir: Path = Field(
        default=Path("./pipelines"),
        description="Output directory for generated pipelines",
    )
    template_dir: Path = Field(
        default=Path(__file__).parent.parent / "pipeline" / "templates"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[Path] = Field(default=None, description="Log file path")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @field_validator("output_dir", "template_dir", "log_file", mode="before")
    def resolve_path(cls, v):
        if v is None:
            return v
        return Path(v).resolve()

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization validation and setup."""
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load environment variables from .env file if it exists
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM-specific configuration."""
        if self.llm_provider == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def validate_llm_config(self) -> None:
        """Validate LLM configuration."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or add it to .env file."
            )


# Global configuration instance
config = Config()
