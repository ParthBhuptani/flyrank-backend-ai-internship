import json

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

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

# Update an existing task
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, request: Request):

    # Find the requested task
    task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    # Return 404 if the task doesn't exist
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    # Read and validate the request body
    try: 
        payload = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must contain valid JSON"}
        )
    
    # Body must be a non-empty JSON object
    if not isinstance(payload, dict) or not payload:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must be a non-empty JSON object"}
        )
    
    # At least one supported field must be provided
    if not any(field in payload for field in ("title", "done")):
        return JSONResponse(
            status_code=400,
            content={"error": "Provide at least one valid field: title or done"}
        )

    # Validate title if provided
    if "title" in payload:
        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"}
            )
    
    # Validate done if provided
    if "done" in payload:
        if not isinstance(payload["done"], bool):
            return JSONResponse(
                status_code=400,
                content={"error":"Done must be a boolean"}
            )
    
    # Update only the provided fields
    if "title" in payload:
        task["title"] = payload["title"].strip()
    
    if "done" in payload:
        task["done"] = payload["done"]
    
    return task

# Delete an existing task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    # Find the task
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            # Remove the task
            tasks.pop(index)

            # Return 204 No Content
            return Response(status_code=204)
    
    # Return 404 if the task doesn't exist
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )