"""
FastAPI Application - HSI Battle Product Strategy API

This application provides an endpoint for processing product-related data from text and/or images,
and generating optimized product strategies using the Gemini API.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from dotenv import load_dotenv
import os
from processing_product import process_combined_input

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="HSI Battle Product Strategy API",
    description="A FastAPI application for processing product data and generating marketing strategies",
    version="2.0.0"
)

# Define port for the server
port = int(os.getenv("PORT", 8000))

# Pydantic models
class ProcessingInput(BaseModel):
    text: str = ""
    image_url: HttpUrl = None
    trace_id: str = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HSI Battle Product Strategy API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "processing_input": "/processing-input"
        },
        "features": {
            "multimodal_processing": "Process text and image simultaneously",
            "ai_strategies": "Gemini-powered marketing strategy generation"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/processing-input")
async def processing_input(request: ProcessingInput):
    """
    Process both image and text input together using Gemini AI.
    Returns enhanced JSON data including image and video descriptions.
    
    Expected input:
    {
        "text": "Product description text",
        "image_url": "https://example.com/image.png",
        "trace_id": "optional-trace-id"
    }
    
    Returns:
    {
        "trace_id": "12345",
        "title": "Enhanced product title",
        "description": "Detailed product description",
        "slogan": "Product slogan",
        "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
        "image_description": "Detailed description for AI image generation",
        "video_description": "Detailed description for AI video generation"
    }
    """
    try:
        # Validate input - at least one of text or image must be provided
        if not request.text.strip() and not request.image_url:
            raise HTTPException(
                status_code=400, 
                detail="Either text or image_url must be provided"
            )
        
        # Process the combined input through Gemini
        result = process_combined_input(
            text=request.text.strip() if request.text else "",
            image_url=str(request.image_url) if request.image_url else "",
            trace_id=request.trace_id
        )
        
        if result.get("processing_status") == "error":
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Unknown processing error")
            )
        
        # Return enhanced JSON data including image and video descriptions
        strategies = result.get("strategies", {})
        return {
            "trace_id": result.get("trace_id"),
            "title": strategies.get("title", ""),
            "description": strategies.get("description", ""),
            "slogan": strategies.get("slogan", ""),
            "hashtags": strategies.get("hashtags", []),
            "image_description": strategies.get("image_description", ""),
            "video_description": strategies.get("video_description", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )