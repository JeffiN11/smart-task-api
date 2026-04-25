from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db, AsyncSessionLocal
from app.models.task import Task, Priority, Status
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.ollama_service import get_ai_priority

router = APIRouter()


async def _apply_ai_priority(task_id: int, title: str, description: str | None):
    async with AsyncSessionLocal() as session:
        result = await session.get(Task, task_id)
        if result is None:
            return
        ai_result = await get_ai_priority(title, description)
        result.priority = Priority(ai_result["priority"])
        result.ai_reasoning = ai_result["reasoning"]
        await session.commit()


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=Priority.pending,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    background_tasks.add_task(
        _apply_ai_priority, task.id, task.title, task.description
    )
    return task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: Status | None = Query(None),
    priority: Priority | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task)
    count_query = select(func.count(Task.id))

    if status:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
        count_query = count_query.where(Task.priority == priority)

    query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    total = (await db.execute(count_query)).scalar_one()
    tasks = (await db.execute(query)).scalars().all()
    return TaskListResponse(total=total, tasks=list(tasks))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    changed_text = False
    if task_in.title is not None and task_in.title != task.title:
        task.title = task_in.title
        changed_text = True
    if task_in.description is not None and task_in.description != task.description:
        task.description = task_in.description
        changed_text = True
    if task_in.status is not None:
        task.status = task_in.status

    if task_in.priority is not None:
        task.priority = task_in.priority
        task.ai_reasoning = "Priority manually overridden."
    elif changed_text:
        task.priority = Priority.pending
        background_tasks.add_task(
            _apply_ai_priority, task.id, task.title, task.description
        )

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()


@router.post("/{task_id}/reprioritize", response_model=TaskResponse)
async def reprioritize_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    ai_result = await get_ai_priority(task.title, task.description)
    task.priority = Priority(ai_result["priority"])
    task.ai_reasoning = ai_result["reasoning"]
    await db.commit()
    await db.refresh(task)
    return task
