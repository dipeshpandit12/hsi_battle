"""
FastAPI Application
A simple FastAPI server with basic endpoints
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from pyngrok import ngrok
from dotenv import load_dotenv
import os
import ssl
import sys
from processing_text.main import process_seller_text
from pydantic import BaseModel, HttpUrl
from processing_image.main import processing_seller_image


# Create FastAPI instance
app = FastAPI(
    title="HSI Battle API",
    description="A FastAPI application for HSI Battle project",
    version="1.0.0"
)

# Load environment variables
load_dotenv()
# Define port for the server
# Try to get port from environment variable, default to 8000 if not set
port = int(os.getenv("PORT", 8000))
# Get ngrok auth token from environment variable
ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")

# Pydantic models
class TextInput(BaseModel):
    text: str

# Pydantic models
class VideoInput(BaseModel):
    url: HttpUrl


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to HSI Battle API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}



#this endpoint receives the users text input entered by the seller in the input box in the seller dashboard in next.js app and and should pass to the seller-text folder main.py file for processing
@app.post("/processing-text")
async def processing_text(request: TextInput):
    return {"received_text": request.text, "message": "Text received successfully", "return_value": process_seller_text(request.text)}



#this endpoiint process the image url as input from the seller dashboard in next.js app and should pass to the image-processing folder main.py file for processing
@app.post("/processing-image")
async def processing_image(request: VideoInput):
    # Import the process_image function at the top of the file
    return {"received_image_url": str(request.url), "message": "image URL received successfully", "return_value": processing_seller_image(request.url)}



if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )