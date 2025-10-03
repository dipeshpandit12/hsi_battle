"""
FastAPI Application
A simple FastAPI server with basic endpoints
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="HSI Battle API",
    description="A FastAPI application for HSI Battle project",
    version="1.0.0"
)


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to HSI Battle API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}



#this endpoint receives the users text input entered by the seller in the input box in the seller dashboard in next.js app



#this endpoint receives the users text input entered by the seller in the input box in the seller dashboard in next.js app


if __name__ == "__main__":
    # This allows running the server with: python3 main.py
    print("Starting FastAPI server...")
    print("API Documentation will be available at: http://localhost:8000/docs")
    print("Alternative docs at: http://localhost:8000/redoc")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )