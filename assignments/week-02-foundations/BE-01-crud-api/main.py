from fastapi import FastAPI, Body, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple in-memory API for managing tasks."
)

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):

    # Convert invalid request body errors into HTTP 400
    if any(
        error.get("loc", [None])[0] == "body"
        for error in exc.errors()
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request body"}
        )

    return await request_validation_exception_handler(request, exc)

# In-memory task storage
tasks = [
    {"id": 1, "title": "Learn Python", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Create a GitHub repository", "done": True}
]

# Root endpoint - API information
@app.get("/")
def read_root():
    """Return basic information about the Task API"""
    return{
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Check whether the Task API is responding"""
    return{
        "status": "ok"
    }

# Get all tasks
@app.get("/tasks")
def get_tasks():
     """Return all tasks stored in memory."""
    return tasks

# Get a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Retrieve a task by its ID."""
    for task in tasks:
        if task["id"] == task_id:
            return task

    
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

# Create a new task
@app.post("/tasks", status_code=201)
def create_task(payload: dict = Body(...)):
    """Create a new task after validating its title."""

    # xtract title from request body
    title = payload.get("title")

    # Validate title
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
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
def update_task(task_id: int, payload: dict = Body(...)):
    """Update the title and/or completion status of a task."""

    # Find the requested task
    task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    # Reject empty or unsupported request bodies
    if not payload or not any(
        field in payload for field in ("title", "done")
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title and/or done"}
        )

    # Validate title
    if "title" in payload:
        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"}
            )

    # Validate completion status
    if "done" in payload and not isinstance(payload["done"], bool):
        return JSONResponse(
            status_code=400,
            content={"error": "Done must be a boolean"}
        )

    # Apply valid updates
    if "title" in payload:
        task["title"] = payload["title"].strip()

    if "done" in payload:
        task["done"] = payload["done"]

    return task

# Delete an existing task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """Delete a task by its ID."""

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
