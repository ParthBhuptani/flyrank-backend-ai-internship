from fastapi import FastAPI

# Create the FastAPI application
app = FastAPI()

#First route
@app.get("/")
def home():
    return{
        "message": "Hello from Task API"
    }