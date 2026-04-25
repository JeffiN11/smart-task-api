from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.routers import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Smart Task API",
    description="AI-powered task manager that auto-prioritizes tasks using a local LLM (Ollama).",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Smart Task API is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
