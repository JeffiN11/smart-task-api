from fastapi import FastAPI
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Task Management API")

@app.get("/")
def root():
    return {"message": "API is running successfully"}