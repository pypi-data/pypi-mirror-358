"""Main FastAPI application for MCP-Opal adapter"""

import logging
import uvicorn
from fastapi import FastAPI
from opal_tools_sdk import ToolsService

from .api.routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app and integrate with Opal Tools SDK
app = FastAPI(
    title="MCP-Opal Adapter Service",
    description=(
        "Bidirectional adapter for converting between MCP and Opal tools"
    ),
    version="1.0.0"
)

# Initialize Opal Tools Service
tools_service = ToolsService(app)

# Include API routes
app.include_router(router) 


def start(host: str = "0.0.0.0", port: int = 8000): 
    uvicorn.run(app, host=host, port=port)
