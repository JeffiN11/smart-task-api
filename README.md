# smart-task-api 🤖

![CI](https://github.com/JeffiN11/smart-task-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)

An AI-powered task management REST API that automatically prioritizes tasks using a **locally-running LLM (Ollama + llama3)** — no API keys, no external services needed.

## How It Works

1. You create a task with a title and description
2. The API saves it instantly and returns a response with `priority: pending`
3. In the background, the task is sent to llama3 running locally via Ollama
4. The AI assigns `low` / `medium` / `high` priority plus a one-line reason
5. The task is updated automatically

## Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI 0.115 (async) |
| Database | PostgreSQL 16 + SQLAlchemy 2 |
| AI Model | Ollama + llama3 (local) |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-asyncio |
| Linting | Ruff |
| CI | GitHub Actions |

## Quick Start

```bash
git clone https://github.com/JeffiN11/smart-task-api.git
cd smart-task-api
docker compose up --build
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /tasks/ | Create task (AI prioritizes in background) |
| GET | /tasks/ | List tasks (filter by status/priority) |
| GET | /tasks/{id} | Get single task |
| PATCH | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task |
| POST | /tasks/{id}/reprioritize | Force AI re-prioritization |

## Example

Create a task:
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Fix login bug", "description": "Users cannot log in on mobile when 2FA is enabled."}'
```

Instant response:
```json
{
  "id": 1,
  "title": "Fix login bug",
  "priority": "pending",
  "ai_reasoning": null
}
```

After AI responds:
```json
{
  "id": 1,
  "title": "Fix login bug",
  "priority": "high",
  "ai_reasoning": "Login failures block all users from accessing the product."
}
```

## Project Structure
## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

## AI Prioritization Logic

- **high** — Urgent, blocking others, production issues, deadlines within 24h
- **medium** — Important but not urgent, should be done this week
- **low** — Nice-to-have, minor improvements, no immediate impact

If Ollama is unavailable, the API gracefully defaults to medium priority and never fails.
