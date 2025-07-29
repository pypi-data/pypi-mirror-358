.PHONY: help build build-dev run test clean docker-build docker-run docker-stop

# Default target
help:
	@echo "MCP-Opal Adapter - Available commands:"
	@echo "  build        - Install dependencies using uv"
	@echo "  build-dev    - Install dependencies including dev tools"
	@echo "  run          - Run development server"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean up generated files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker Compose services"

# Development
build:
	uv sync

build-dev:
	uv sync --extra dev

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Docker
docker-build:
	docker build -t mcp-opal-adapter .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

# Configuration examples
configure-weather:
	curl -X POST http://localhost:8000/configure \
		-H "Content-Type: application/json" \
		-d @examples/weather_tool_config.json

configure-calculator:
	curl -X POST http://localhost:8000/configure \
		-H "Content-Type: application/json" \
		-d @examples/calculator_tool_config.json

# Health checks
health:
	curl http://localhost:8000/health

status:
	curl http://localhost:8000/status

discovery:
	curl http://localhost:8000/discovery

# Tool calls
call-weather:
	curl -X POST http://localhost:8000/tools/weather_lookup \
		-H "Content-Type: application/json" \
		-d '{"location": "New York", "units": "imperial"}'

call-calculator:
	curl -X POST http://localhost:8000/tools/calculator \
		-H "Content-Type: application/json" \
		-d '{"expression": "2 + 2 * 3", "precision": 2}' 