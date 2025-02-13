from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings"""
    # App settings
    app_name: str = Field(default="VLM Image Analysis API", description="Name of the application")
    api_version: str = Field(default="v1", description="API version")
    host: str = Field(default="127.0.0.1", description="Host to run the application on")
    port: int = Field(default=8000, description="Port to run the application on")
    
    # Model settings
    model_name: str = Field(default="llava", description="Name of the Ollama model to use")
    model_temperature: float = Field(default=0.0, description="Temperature for model generation")
    
    # Debug settings
    debug: bool = Field(default=False, description="Debug mode")
    
    # CORS settings
    allowed_origins: List[str] = Field(
        default=["*"],
        description="List of allowed origins for CORS"
    )
    allowed_methods: List[str] = Field(
        default=["*"],
        description="List of allowed HTTP methods for CORS"
    )
    allowed_headers: List[str] = Field(
        default=["*"],
        description="List of allowed HTTP headers for CORS"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Loaded settings: MODEL_NAME={self.model_name}")

settings = Settings()
logger.info(f"Settings initialized with model_name: {settings.model_name}")