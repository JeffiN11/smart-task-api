from fastapi import FastAPI

app = FastAPI(title="Smart Task Management API")

@app.get("/")
def root():
    return {"message": "API is running successfully"}