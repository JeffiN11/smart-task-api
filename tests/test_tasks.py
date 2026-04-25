import pytest
from unittest.mock import patch, AsyncMock

MOCK_AI_RESULT = {"priority": "high", "reasoning": "Mocked AI response for testing."}


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_task(client):
    with patch("app.routers.tasks.get_ai_priority", new_callable=AsyncMock) as mock_ai:
        mock_ai.return_value = MOCK_AI_RESULT
        response = await client.post("/tasks/", json={
            "title": "Fix critical login bug",
            "description": "Users cannot log in on mobile.",
        })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Fix critical login bug"
    assert data["priority"] == "pending"


@pytest.mark.asyncio
async def test_get_task(client):
    create_resp = await client.post("/tasks/", json={"title": "Test task"})
    task_id = create_resp.json()["id"]
    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    response = await client.get("/tasks/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks(client):
    await client.post("/tasks/", json={"title": "Task A"})
    await client.post("/tasks/", json={"title": "Task B"})
    response = await client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_update_task_status(client):
    create_resp = await client.post("/tasks/", json={"title": "Task to update"})
    task_id = create_resp.json()["id"]
    response = await client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_update_task_manual_priority(client):
    create_resp = await client.post("/tasks/", json={"title": "Task to prioritize"})
    task_id = create_resp.json()["id"]
    response = await client.patch(f"/tasks/{task_id}", json={"priority": "low"})
    assert response.status_code == 200
    assert response.json()["priority"] == "low"
    assert response.json()["ai_reasoning"] == "Priority manually overridden."


@pytest.mark.asyncio
async def test_delete_task(client):
    create_resp = await client.post("/tasks/", json={"title": "Task to delete"})
    task_id = create_resp.json()["id"]
    delete_resp = await client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 204
    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_reprioritize_task(client):
    create_resp = await client.post("/tasks/", json={"title": "Reprioritize me"})
    task_id = create_resp.json()["id"]
    with patch("app.routers.tasks.get_ai_priority", new_callable=AsyncMock) as mock_ai:
        mock_ai.return_value = MOCK_AI_RESULT
        response = await client.post(f"/tasks/{task_id}/reprioritize")
    assert response.status_code == 200
    assert response.json()["priority"] == "high"


@pytest.mark.asyncio
async def test_filter_by_status(client):
    await client.post("/tasks/", json={"title": "Todo task", "status": "todo"})
    await client.post("/tasks/", json={"title": "Done task", "status": "done"})
    response = await client.get("/tasks/?status=todo")
    assert response.status_code == 200
    assert response.json()["total"] == 1
