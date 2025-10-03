"""
FastAPI Application - HSI Battle Product Strategy API

This application provides endpoints for processing product-related data from text or images,
and generating optimized product strategies using the Gemini API.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from dotenv import load_dotenv
import os
from processing_text.main import process_seller_text
from processing_image.main import processing_seller_image

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="HSI Battle Product Strategy API",
    description="A FastAPI application for processing product data and generating marketing strategies",
    version="1.0.0"
)

# Define port for the server
port = int(os.getenv("PORT", 8000))

# Pydantic models
class TextInput(BaseModel):
    text: str

class ImageInput(BaseModel):
    image_url: HttpUrl

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HSI Battle Product Strategy API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "processing_text": "/processing-text",
            "processing_image": "/processing-image"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/processing-text")
async def processing_text(request: TextInput):
    """
    Process raw text input, enhance it for clarity, and forward to processing-product.
    
    Expected input:
    {
        "text": "Long unstructured text about the product..."
    }
    
    Returns:
    {
        "trace_id": "12345",
        "confidence": 0.92,
        "processing_status": "success"
    }
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        result = process_seller_text(request.text)
        
        if result.get("processing_status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown processing error"))
        
        # Return only the essential information as specified in README
        return {
            "trace_id": result.get("trace_id"),
            "confidence": result.get("confidence", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/processing-image")
async def processing_image(request: ImageInput):
    """
    Process image URL, analyze using Gemini Vision, and forward to processing-product.
    
    Expected input:
    {
        "image_url": "https://example.com/image.png"
    }
    
    Returns:
    {
        "trace_id": "12345",
        "warnings": []
    }
    """
    try:
        result = processing_seller_image(request.image_url)
        
        if result.get("processing_status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown processing error"))
        
        # Return only the essential information as specified in README
        return {
            "trace_id": result.get("trace_id"),
            "warnings": result.get("warnings", [])
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