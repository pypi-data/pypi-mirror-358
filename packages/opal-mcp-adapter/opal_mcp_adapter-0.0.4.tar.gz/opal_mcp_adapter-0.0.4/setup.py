from setuptools import setup, find_packages

setup(
    name="opal-mcp-adapter",
    version="0.0.4",
    description=(
        "Bidirectional adapter for converting between MCP and Opal tools"
    ),
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "httpx>=0.25.0",
        "mcp>=1.9.4",
        "optimizely-opal-opal-tools-sdk>=0.1.1.dev0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6",
        "pyyaml>=6.0.1",
        "uvicorn>=0.24.0",
    ],
    entry_points={
        "console_scripts": [
            "opal-mcp-adapter=opal_mcp_adapter.server:start",
        ],
    },
    python_requires=">=3.10",
)