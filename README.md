# smart-task-api

An AI-powered task management REST API built with FastAPI, PostgreSQL, and Ollama (llama3). Tasks are automatically prioritized (Low / Medium / High) by a locally-running LLM the moment they are created.

## Tech Stack
- FastAPI 0.115
- PostgreSQL 16 + SQLAlchemy 2 (async)
- Ollama + llama3 (local LLM)
- Docker + Docker Compose
- pytest + pytest-asyncio
- GitHub Actions CI

## Quick Start

```bash
docker compose up --build
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /tasks/ | Create task (AI prioritizes async) |
| GET | /tasks/ | List tasks |
| GET | /tasks/{id} | Get task |
| PATCH | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task |
| POST | /tasks/{id}/reprioritize | Force AI re-prioritization |

## Run Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```
