## Check the tools

```
python3 --version
python -m pip --version
git --version
docker --version
docker compose version
```

Docker should be able to run a test container. Run the following once if Docker is installed but not yet verified:

```
docker run hello-world
```

**Docker permissions**

If Docker reports permission denied for /var/run/docker.sock, this is an operating-system/Docker access issue. Use the approved university setup or ask the IT administrator. Do not bypass university security controls.

# Demonstration 0 - Prepare the Project

## 0.1 Confirm the project root

Open a terminal. Because the path contains spaces, quote it or escape the spaces. Use the path that applies to your machine:

```
cd "$HOME/Agentic AI SE/Week 04/Phase 03"
pwd
ls -la
```

The current directory should be Phase 03 and should contain (or be ready to contain) src/, tests/, deployment/, requirements.txt, and pyproject.toml.

## 0.2 Create directories

```
mkdir -p src/ai_service/api
mkdir -p src/ai_service/services
mkdir -p src/ai_service/config
mkdir -p src/ai_service/utils
mkdir -p tests deployment
touch src/ai_service/__init__.py
touch src/ai_service/api/__init__.py
touch src/ai_service/services/__init__.py
touch src/ai_service/config/__init__.py
touch src/ai_service/utils/__init__.py
```

## 0.3 Create and activate a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
python --version
```

The prompt should show (.venv). On Windows PowerShell, use .venv\\Scripts\\Activate.ps1 instead of the Linux source command.

## 0.4 Create requirements.txt

```
fastapi
uvicorn
python-dotenv
pytest
httpx
```

Save the text above as requirements.txt, then install it:

```
python -m pip install -r requirements.txt
```

## 0.5 Create pyproject.toml

```
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

This tells pytest that the application package lives inside src/. It should allow pytest -q to work from the project root without a manual PYTHONPATH setting.

## 0.6 Verify the package path

```
PYTHONPATH=src python -c "import ai_service; print(ai_service.__file__)"
```

Expected: the printed path ends with src/ai_service/\__init_\_.py.

# Demonstration 1 - Understand the Architecture

## 1.1 The component map

```
Client (browser, curl, Postman/Bruno)
          | HTTP request
          v
API component: src/ai_service/api/routes.py
          | calls a service method
          v
Service component: src/ai_service/services/ai_service.py
          | classification rules (Week 04 placeholder)
          v
Response returned through FastAPI
```

The configuration component (config/settings.py) supplies settings. The logging utility (utils/logging.py) supplies a shared logger. The Docker deployment packages the application and its dependencies so the same service can run in an isolated container.

## 1.2 Component versus interface

| **Term**             | **Meaning in this lab**                                    | **Example**                                                      |
| -------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------- |
| Component            | A part with a defined responsibility.                      | routes.py, AIService, settings.py, logger configuration          |
| Interface / contract | A defined way for another component or client to interact. | HTTP endpoints and the AIService.classify(text) method signature |
| Implementation       | Code that performs the behavior behind the contract.       | The keyword rules inside AIService.classify                      |
| Configuration        | Values supplied without editing application logic.         | APP_NAME and APP_VERSION in the environment                      |
| Deployment unit      | The packaged runtime artifact.                             | week04-ai-service Docker image                                   |

The API is an external interface: clients agree to call a path using an HTTP method and receive a response. The service method is an internal programming interface. In a later extension, students can create a Python Protocol for a classifier and inject a rule-based, ML-based, or LLM-based implementation behind that contract.

## 1.3 The endpoints

| **Method** | **Path**           | **Purpose**                   | **Expected result**        |
| ---------- | ------------------ | ----------------------------- | -------------------------- |
| GET        | /                  | Service identity              | JSON message and version   |
| GET        | /health            | Health status                 | {"status":"healthy"}       |
| POST       | /classify?text=... | Classify text                 | Original text and category |
| GET        | /docs              | Interactive API documentation | Swagger UI page            |

# Demonstration 2 - Configuration and Logging

## 2.1 Create .env.example

```
APP_NAME=Week 04 AI Service
APP_VERSION=1.0.0
DEBUG=false
```

Create a local .env file from the example. The .env file is for local values and must not be committed if it contains secrets.

```
cp .env.example .env
```

## 2.2 Protect local settings with .gitignore

```
.env
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
```

The actual .env file stays on the developer machine and should not be committed. Commit .env.example instead, because it documents the required variable names without containing secrets.

## 2.3 Implement settings.py

Save this code as src/ai_service/config/settings.py:

```
import os
```

```
from dotenv import load_dotenv
```

```
# Load .env for local development; Docker can also inject environment variables.
load_dotenv()
```

```
class Settings:
    """Central application settings loaded from the environment."""
```

```
    APP_NAME: str = os.getenv("APP_NAME", "Week 04 AI Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
```

```
settings = Settings()
```

The default values make local execution possible even if a variable is absent. DEBUG is converted from the text true/false to a Python boolean.

## 2.4 Implement logging.py

Save this code as src/ai_service/utils/logging.py:

```
import logging
import sys
```

```
def configure_logging() -> logging.Logger:
    """Configure logging to stdout, including inside a container."""
    logger = logging.getLogger("ai_service")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
```

# Demonstration 3 - Build the Service and API

## 3.1 Implement services/ai_service.py

Save this complete code as src/ai_service/services/ai_service.py. The classification rules are deliberately deterministic so every student can reproduce the same output without an LLM or Internet connection.

```
import logging
```

```
class AIService:
    """Application service containing the Week 04 demo logic."""
```

```
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
```

```
    def classify(self, text: str) -> dict[str, str]:
        """Classify input text using simple keyword rules."""
```

```
        if not isinstance(text, str):
            raise TypeError("text must be a string")
```

```
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty.")
```

```
        normalized_text = text.lower()
        self.logger.info("Classifying text")
```

```
        if "password" in normalized_text:
            category = "account"
        elif "fee" in normalized_text or "payment" in normalized_text:
            category = "finance"
        elif (
            "server" in normalized_text
            or "api" in normalized_text
            or "error" in normalized_text
        ):
            category = "technical"
        elif "admission" in normalized_text:
            category = "admission"
        else:
            category = "other"
```

```
        self.logger.info("Classification completed: %s", category)
        return {"text": text, "category": category}
```

## 3.2 Implement api/routes.py

Save as src/ai_service/api/routes.py:

```
from fastapi import APIRouter, HTTPException
```

```
from ai_service.config.settings import settings
from ai_service.services.ai_service import AIService
from ai_service.utils.logging import configure_logging
```

```
router = APIRouter()
logger = configure_logging()
ai_service = AIService(logger)
```

```
@router.get("/")
def root() -> dict[str, str]:
    return {
        "message": "AI Service is running",
        "version": settings.APP_VERSION,
    }
```

```
@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
```

```
@router.post("/classify")
def classify(text: str) -> dict[str, str]:
    try:
        return ai_service.classify(text)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

In this demonstration, text is a query parameter, so it can be tested at /classify?text=.... The interactive /docs page documents this parameter automatically. A later lab can change the request to a JSON/Pydantic body.

## 3.3 Implement main.py with a lifespan handler

Save as src/ai_service/main.py. The lifespan handler is used instead of the deprecated @app.on_event startup decorator.

```
from contextlib import asynccontextmanager
```

```
from fastapi import FastAPI
```

```
from ai_service.api.routes import router
from ai_service.config.settings import settings
from ai_service.utils.logging import configure_logging
```

```
logger = configure_logging()
```

```
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run setup before serving and cleanup when shutting down."""
    logger.info(
        "Starting %s version %s",
        settings.APP_NAME,
        settings.APP_VERSION,
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)
```

```
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Week 04 Software Architecture and Cloud Foundations",
    debug=settings.DEBUG,
    lifespan=lifespan,
)
```

```
app.include_router(router)
```

# Demonstration 4 - Automated Testing

## 4.1 Implement tests/test_ai_service.py

```
import logging
```

```
from fastapi.testclient import TestClient
```

```
from ai_service.main import app
from ai_service.services.ai_service import AIService
```

```
client = TestClient(app)
```

```
def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "AI Service is running"
```

```
def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

```
def test_password_classification() -> None:
    response = client.post("/classify", params={"text": "I forgot my password"})
    assert response.status_code == 200
    assert response.json()["category"] == "account"
```

```
def test_fee_classification() -> None:
    response = client.post("/classify", params={"text": "I have a fee problem"})
    assert response.status_code == 200
    assert response.json()["category"] == "finance"
```

```
def test_technical_classification() -> None:
    response = client.post("/classify", params={"text": "The server is down"})
    assert response.status_code == 200
    assert response.json()["category"] == "technical"
```

```
def test_unknown_classification() -> None:
    response = client.post("/classify", params={"text": "I need information"})
    assert response.status_code == 200
    assert response.json()["category"] == "other"
```

```
def test_empty_text_returns_400() -> None:
    response = client.post("/classify", params={"text": ""})
    assert response.status_code == 400
```

```
def test_service_directly() -> None:
    service = AIService(logging.getLogger("test"))
    result = service.classify("I forgot my password")
    assert result == {
        "text": "I forgot my password",
        "category": "account",
    }
```

## 4.2 Run tests from the project root

```
pytest -q
```

Expected result: eight passing tests. A warning about the test client dependency is not a failure if the test summary still reports eight passed. If pytest says ModuleNotFoundError: No module named ai_service, confirm pyproject.toml contains the pytest configuration shown in Demonstration 0 and that you are running from the project root. As a diagnostic, run PYTHONPATH=src pytest -q.

## 4.3 What do these tests prove?

The endpoint tests verify HTTP status codes and response payloads. The classification tests verify the deterministic rules. The validation test confirms that empty input becomes HTTP 400. The direct service test confirms that the application logic can be exercised without an HTTP request.

# Demonstration 5 - Run and Test the Local API

## 5.1 Start Uvicorn

```
uvicorn --app-dir src ai_service.main:app --reload
```

The terminal should report that Uvicorn is running on <http://127.0.0.1:8000>. Keep this terminal open. The --app-dir src option adds src/ to Python import lookup, while ai_service.main:app identifies the module and FastAPI object.

## 5.2 Try the endpoints

| **Endpoint**   | **Command or action**               | **Expected result**           |
| -------------- | ----------------------------------- | ----------------------------- |
| GET /          | curl <http://127.0.0.1:8000/>       | JSON with message and version |
| GET /health    | curl <http://127.0.0.1:8000/health> | {"status":"healthy"}          |
| GET /docs      | Open in a browser                   | Swagger UI                    |
| POST /classify | Use command below                   | JSON with text and category   |

```
curl -X POST "http://127.0.0.1:8000/classify?text=I%20forgot%20my%20password"
```

Expected response:

```
{
  "text": "I forgot my password",
  "category": "account"
}
```

Try a technical request:

```
curl -X POST "http://127.0.0.1:8000/classify?text=The%20server%20is%20down"
```

Expected category: technical.

## 5.3 Observe logs

After submitting a classification request, inspect the Uvicorn terminal. The service should print log messages for classification start and completion. These messages are operational events; they are not returned as part of the user-facing JSON response.

# Demonstration 6 - Containerize the Service

## 6.1 Create deployment/Dockerfile

```
FROM python:3.12-slim
```

```
WORKDIR /app
```

```
COPY requirements.txt .
```

```
RUN pip install --no-cache-dir -r requirements.txt
```

```
COPY src ./src
```

```
ENV PYTHONPATH=/app/src
```

```
EXPOSE 8000
```

```
CMD ["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Important: keep the JSON-array CMD on one line. Do not place each quoted argument on a separate Dockerfile instruction line.

## 6.2 Create .dockerignore

```
.venv
venv
__pycache__
*.pyc
.pytest_cache
.git
.gitignore
.env
tests
README.md
architecture.md
```

The .dockerignore file prevents local environments, source-control history, test files, and the local .env from being copied into the Docker build context/image.

## 6.3 Build the image

Run from Phase 03/, not from deployment/:

```
docker build -f deployment/Dockerfile -t week04-ai-service .
```

The dot at the end is the build context: the project root. Docker needs access to requirements.txt and src/ from that directory.

## 6.4 Verify the image

```
docker images
```

Look for week04-ai-service with the latest tag.

## 6.5 Run the container

```
docker run --rm -p 8000:8000 week04-ai-service
```

Open a second terminal and verify:

```
curl http://127.0.0.1:8000/health
curl -X POST "http://127.0.0.1:8000/classify?text=The%20server%20is%20down"
```

The first command should return healthy; the second should return category technical. In -p 8000:8000, the left-hand port is on the host and the right-hand port is inside the container. Uvicorn listens on 0.0.0.0 inside the container. Stop the foreground container with Ctrl+C. Because --rm was used, Docker removes that container when it stops, but the image remains.

# Demonstration 7 - Docker Compose and Environment Configuration

## 7.1 Create .env

Docker Compose will fail if the configured env_file does not exist. Create the local file from the example in the project root:

```
cp .env.example .env
ls -la .env
```

The .env file is not the same as .env.example: .env.example is a shareable template, while .env contains the local values. Do not commit .env.

## 7.2 Create deployment/docker-compose.yml

```
services:
  ai-service:
    build:
      context: ..
      dockerfile: deployment/Dockerfile
```

```
    container_name: week04-ai-service
```

```
    ports:
      - "8000:8000"
```

```
    env_file:
      - ../.env
```

```
    restart: unless-stopped
```

Because the Compose file is in deployment/, context: .. means the parent directory (the project root). The env_file path ../.env also resolves from the Compose file directory. These paths are the most common source of errors in this project.

## 7.3 Validate Compose configuration

```
docker compose -f deployment/docker-compose.yml config
```

If Compose reports that .env cannot be found, check that you created it at the project root and that the YAML uses ../.env. If the YAML is malformed, the config command will report the relevant error before a container starts.

## 7.4 Build and start the service

```
docker compose -f deployment/docker-compose.yml up --build
```

Leave this terminal running. Open a second terminal and test the health endpoint:

```
curl http://127.0.0.1:8000/health
```

## 7.5 Inspect service state and logs

```
docker ps
docker logs week04-ai-service
```

If the container exits, read the logs before rebuilding.

## 7.6 Stop the service

```
docker compose -f deployment/docker-compose.yml down
```

Compose stops and removes the container. The built image remains available locally.

# Demonstration 8 - Document the Architecture

## 8.1 Create architecture.md

```
# Week 04 AI Service Architecture
```

```
## Purpose
This project packages a simple text-classification capability as a testable REST service and Docker container.
```

```
## Request flow
Client -> HTTP -> FastAPI route -> AIService -> classification result -> HTTP response.
```

```
## Components
- API layer: src/ai_service/api/routes.py handles HTTP requests, responses, and HTTP error translation.
- Service layer: src/ai_service/services/ai_service.py contains the classification operation.
- Configuration: src/ai_service/config/settings.py loads environment values.
- Logging: src/ai_service/utils/logging.py configures console logging.
- Application entry point: src/ai_service/main.py creates the FastAPI application and lifecycle handler.
- Tests: tests/test_ai_service.py validates the API and service.
- Deployment: deployment/Dockerfile and deployment/docker-compose.yml package and run the service.
```

```
## Interfaces
- External interface: GET /, GET /health, POST /classify.
- Service interface: AIService.classify(text) -> dictionary containing text and category.
```

```
## Configuration
APP_NAME, APP_VERSION, and DEBUG are environment-based settings. The .env file is local and must not be committed.
```

```
## Containerization
Docker builds the image. Port mapping 8000:8000 forwards host traffic to the container. Docker Compose passes environment values and manages the service lifecycle.
```

```
## Future extension
The deterministic classification implementation can later be replaced behind an internal model/classifier interface. Week 05 introduces a local LLM via Ollama; later weeks add agent loops, tools, memory, RAG, and orchestration.
```

This document is a concise design record. Students should update it if their actual implementation differs from the guide.

## 8.2 Create README.md

```
# Week 04 - Containerized AI Service
```

```
## Purpose
Demonstrates layered application architecture, REST APIs, configuration, logging, tests, Docker, and Docker Compose.
```

```
## Requirements
- Python 3.12+
- Docker Engine/Desktop and Docker Compose
```

````
## Local setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
pytest -q
```
````

````
## Run locally
```bash
uvicorn --app-dir src ai_service.main:app --reload
```
Open http://127.0.0.1:8000/docs.
````

````
## Docker
```bash
docker build -f deployment/Dockerfile -t week04-ai-service .
docker run --rm -p 8000:8000 week04-ai-service
```
````

````
## Docker Compose
```bash
docker compose -f deployment/docker-compose.yml up --build
docker compose -f deployment/docker-compose.yml down
```
````

# Troubleshooting Guide

| **Symptom**                                             | **Likely cause**                                                                                                         | **Resolution**                                                                                                                                                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ModuleNotFoundError: No module named ai_service         | src/ is not on the Python import path, or command is run from the wrong directory.                                       | Run from project root. Use uvicorn --app-dir src ai_service.main:app --reload. Ensure pyproject.toml has pythonpath = \["src"\]. For tests, use PYTHONPATH=src pytest -q as a diagnostic. |
| ModuleNotFoundError: No module named src                | An import starts with from src.ai_service....                                                                            | Change imports to from ai_service.... The package name is ai_service, not src.ai_service.                                                                                                 |
| Dockerfile parse error: unknown instruction: "uvicorn", | CMD JSON array was split into multiple Dockerfile instruction lines or the saved file differs from the intended content. | Put CMD \["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"\] on one line. Inspect with nl -ba deployment/Dockerfile.                                               |
| .env not found                                          | Compose env_file path is wrong or file is absent.                                                                        | From project root run cp .env.example .env. In deployment/docker-compose.yml, use env_file: - ../.env.                                                                                    |
| COPY requirements.txt failed                            | Docker build started from deployment/ or build context is wrong.                                                         | Build from project root using docker build -f deployment/Dockerfile -t week04-ai-service .                                                                                                |
| Port 8000 already allocated                             | Another local server/container is using port 8000.                                                                       | Stop the other process/container, or temporarily publish another host port such as -p 8001:8000 and visit port 8001.                                                                      |
| Container starts then exits                             | Application import/configuration error or runtime exception.                                                             | Run docker logs week04-ai-service. Verify the source files and their import paths.                                                                                                        |
| Docker socket permission denied                         | Current Linux user does not have permission to use Docker.                                                               | Use the university-approved Docker access procedure or contact IT. Do not bypass system controls.                                                                                         |
| Deprecation warning but tests pass                      | A dependency reports a recommended replacement API/package.                                                              | Check the final pytest summary. A warning is not a failed test; keep the class dependency environment consistent.                                                                         |

## Useful diagnostics

```
pwd
find . -maxdepth 4 -type f | sort
cat pyproject.toml
nl -ba deployment/Dockerfile
docker images
docker ps -a
docker logs week04-ai-service
```

# Student Exercises

## Exercise 1 - Extend classification

Add a category called facilities for messages containing the word lab or classroom. Add a pytest test that proves the new behavior. Place the new condition before the final else branch.

## Exercise 2 - Add a new endpoint

Implement GET /version. It should return the configured APP_VERSION from settings, rather than hard-coding the version in the route. Add a test for the endpoint.

## Exercise 3 - Configuration experiment

Change APP_NAME in .env, restart the local service, and observe the API title and startup log. Explain why the Python source does not need to change.

## Exercise 4 - Container experiment

Build the image, run it, stop it, and run it again. Explain the difference between a Docker image and a container. Explain what --rm does.

## Exercise 5 - Model interface design

Without changing the core submission, sketch a future interface for a classifier with a classify(text) method. Explain how a rule-based implementation could later be replaced by an ML model or a local LLM without changing the HTTP contract. This is a design exercise preparing for Week 05.

# Required submission checklist

- \[ \] The project structure matches the required layout.
- \[ \] requirements.txt and pyproject.toml are included.
- \[ \] .env.example is included and .env is excluded by .gitignore.
- \[ \] The application starts locally using the documented Uvicorn command.
- \[ \] GET / and GET /health return the expected responses.
- \[ \] POST /classify returns correct categories for sample inputs.
- \[ \] pytest -q passes all tests.
- \[ \] Docker image builds successfully from the project root.
- \[ \] Container works through port mapping 8000:8000.
- \[ \] Docker Compose starts and stops the service successfully.
- \[ \] Container logs are inspectable.
- \[ \] README.md contains setup and run instructions.
- \[ \] architecture.md documents components, interfaces, request flow, and deployment.

## Suggested evidence to submit

- Screenshot or terminal output showing successful pytest run.
- Screenshot of /docs or a tested API request and response.
- Terminal output showing a successful Docker build.
- docker ps output while the container is running.
- A short paragraph explaining the API layer, service layer, configuration, logging, and Docker boundary.

# Viva / Demonstration Questions

1. What is the difference between code structure and system architecture?
2. What responsibility belongs in routes.py and what belongs in ai_service.py?
3. What is the difference between a component, an interface, and an implementation?
4. Why do we use environment variables for configuration?
5. Why should .env not be committed to GitHub or copied into a production image?
6. Why does Docker need the project root as the build context?
7. What does PYTHONPATH=/app/src do in the Dockerfile?
8. What is the difference between a Docker image and a container?
9. What does the port mapping 8000:8000 mean?
10. Why are application logs sent to stdout in a container?
11. How could the classification component be replaced by a local LLM in Week 05?
12. Which checks would you run if the service starts locally but fails in Docker?

# Completion Criteria

**You have completed Week 04 when...**

the local tests pass, the API responds, the Docker image builds, the container serves the health endpoint, Compose can start/stop the service, logs are visible, and README.md plus architecture.md explain how the system is structured.

End of Week 04 Student Lab Guide.