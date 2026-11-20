from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# In-memory task storage
tasks = [
    {"id": 1, "title": "Learn Python", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Create a GitHub repository", "done": True}
]

# Root endpoint - API information
@app.get("/")
def read_root():
    return{
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return{
        "status": "ok"
    }

# Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# Get a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )