# Week 04 AI Service Architecture

## Purpose
This project packages a simple text-classification capability as a testable REST service and Docker container.

## Request flow
Client -> HTTP -> FastAPI route -> AIService -> classification result -> HTTP response.

## Components
- API layer: src/ai_service/api/routes.py handles HTTP requests, responses, and HTTP error translation.
- Service layer: src/ai_service/services/ai_service.py contains the classification operation.
- Configuration: src/ai_service/config/settings.py loads environment values.
- Logging: src/ai_service/utils/logging.py configures console logging.
- Application entry point: src/ai_service/main.py creates the FastAPI application and lifecycle handler.
- Tests: tests/test_ai_service.py validates the API and service.
- Deployment: deployment/Dockerfile and deployment/docker-compose.yml package and run the service.

## Interfaces
- External interface: GET /, GET /health, GET /version, POST /classify.
- Service interface: AIService.classify(text) -> dictionary containing text and category.

## Configuration
APP_NAME, APP_VERSION, and DEBUG are environment-based settings. The .env file is local and must not be committed.

## Containerization
Docker builds the image. Port mapping 8000:8000 forwards host traffic to the container. Docker Compose passes environment values and manages the service lifecycle.

## Future extension
The deterministic classification implementation can later be replaced behind an internal model/classifier interface. Week 05 introduces a local LLM via Ollama; later weeks add agent loops, tools, memory, RAG, and orchestration.
