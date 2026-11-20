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

# Create a new task
@app.post("/tasks", status_code=201)
def create_task(payload: dict):

    # xtract title from request body
    title = payload.get("title")

    # Validate title
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=404,
            content={
                "error": "Title is required and must be a non-empty string"
            }        
        )

    # Generate the next available ID
    next_id = max(
        (task["id"] for task in tasks),
        default=0
    ) + 1

    # Create the new task
    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }

    # Add task to the list
    tasks.append(new_task)

    return new_task