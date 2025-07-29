"""Application settings and configuration"""

from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    # MCP settings
    mcp_timeout: float = 30.0
    
    # Opal Tools SDK settings
    opal_tools_discovery_url: str = "/discovery"
    
    class Config:
        env_file = ".env"
        case_sensitive = False 