# Week 04 - Containerized AI Service

## Purpose
Demonstrates layered application architecture, REST APIs, configuration, logging, tests, Docker, and Docker Compose.

## Requirements
- Python 3.12+
- Docker Engine/Desktop and Docker Compose

## Local setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
pytest -q
```

## Run locally
```bash
uvicorn --app-dir src ai_service.main:app --reload
```
Open http://127.0.0.1:8000/docs.

## Docker
```bash
docker build -f deployment/Dockerfile -t week04-ai-service .
docker run --rm -p 8000:8000 week04-ai-service
```

## Docker Compose
```bash
docker compose -f deployment/docker-compose.yml up --build
docker compose -f deployment/docker-compose.yml down
```
