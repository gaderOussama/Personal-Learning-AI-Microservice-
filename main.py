"""
main.py
Entry point for the AI Study Agent FastAPI application.
"""

from fastapi import FastAPI

app = FastAPI()

# Future endpoints for scheduling study sessions will be added here.

@app.get("/")
def read_root():
    """Root endpoint for health check."""
    return {"message": "AI Study Agent is running."}
