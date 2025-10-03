"""
FastAPI Application - HSI Battle Product Strategy API

This application provides an endpoint for processing product-related data from text and/or images,
and generating optimized product strategies using the Gemini API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import uvicorn
from dotenv import load_dotenv
import os
from processing_product import process_combined_input, generate_image_from_description, generate_video_from_description

# Load environment variables
load_dotenv()

# Create directories for generated content
GENERATED_VIDEOS_DIR = "generated_videos"
GENERATED_IMAGES_DIR = "generated_images"

# Create directories if they don't exist
os.makedirs(GENERATED_VIDEOS_DIR, exist_ok=True)
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

# Create FastAPI instance
app = FastAPI(
    title="HSI Battle Product Strategy API",
    description="A FastAPI application for processing product data and generating marketing strategies",
    version="2.0.0"
)

# Mount static files for serving generated content
app.mount("/downloads/videos", StaticFiles(directory=GENERATED_VIDEOS_DIR), name="videos")
app.mount("/downloads/images", StaticFiles(directory=GENERATED_IMAGES_DIR), name="images")

# Define port for the server
port = int(os.getenv("PORT", 8000))

# Pydantic models
class ProcessingInput(BaseModel):
    text: str = ""
    image_url: HttpUrl = None
    trace_id: str = None

    

class ImageGenerationInput(BaseModel):
    description: str
    width: int = 1024
    height: int = 1024
    trace_id: str = None

class VideoGenerationInput(BaseModel):
    description: str
    duration_seconds: int = 4
    aspect_ratio: str = "16:9"
    trace_id: str = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HSI Battle Product Strategy API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "processing_input": "/processing-input",
            "generate_image": "/generate-image",
            "generate_video": "/generate-video",
            "downloads": "/downloads/{type}/{filename}"
        },
        "features": {
            "multimodal_processing": "Process text and image simultaneously",
            "ai_strategies": "Gemini-powered marketing strategy generation",
            "image_generation": "Stability AI-powered image generation from text descriptions",
            "video_generation": "Gemini-enhanced video concept generation with professional cinematography techniques"
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

@app.post("/generate-image")
async def generate_image(request: ImageGenerationInput):
    """
    Generate an image from a text description using Stability AI.
    
    Expected input:
    {
        "description": "A detailed description of the image to generate",
        "width": 1024,
        "height": 1024,
        "trace_id": "optional-trace-id"
    }
    
    Returns:
    {
        "trace_id": "12345",
        "generation_status": "success",
        "image_url": "data:image/png;base64,<base64_data>",
        "image_base64": "<base64_data>",
        "description": "The description used for generation",
        "width": 1024,
        "height": 1024,
        "seed": 123456789,
        "finish_reason": "SUCCESS"
    }
    """
    try:
        # Validate input
        if not request.description.strip():
            raise HTTPException(
                status_code=400, 
                detail="Description cannot be empty"
            )
        
        # Validate dimensions
        if request.width < 64 or request.width > 1536 or request.width % 64 != 0:
            raise HTTPException(
                status_code=400, 
                detail="Width must be between 64 and 1536 and divisible by 64"
            )
        
        if request.height < 64 or request.height > 1536 or request.height % 64 != 0:
            raise HTTPException(
                status_code=400, 
                detail="Height must be between 64 and 1536 and divisible by 64"
            )
        
        # Generate the image
        result = generate_image_from_description(
            description=request.description.strip(),
            width=request.width,
            height=request.height,
            trace_id=request.trace_id
        )
        
        if result.get("generation_status") == "error":
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Unknown image generation error")
            )
        
        # Return the generated image data
        return {
            "trace_id": result.get("trace_id"),
            "generation_status": result.get("generation_status"),
            "image_url": result.get("image_url"),
            "image_base64": result.get("image_base64"),
            "download_url": result.get("download_url"),
            "local_path": result.get("local_path"),
            "file_size": result.get("file_size"),
            "description": result.get("description"),
            "width": result.get("width"),
            "height": result.get("height"),
            "seed": result.get("seed"),
            "finish_reason": result.get("finish_reason")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/generate-video")
async def generate_video(request: VideoGenerationInput):
    """
    Generate a video from a text description using Gemini AI for enhancement
    and professional video generation techniques.
    
    Expected input:
    {
        "description": "A detailed description of the video to generate",
        "duration_seconds": 4,
        "aspect_ratio": "16:9",
        "trace_id": "optional-trace-id"
    }
    
    Returns:
    {
        "trace_id": "12345",
        "generation_status": "success",
        "original_description": "Original user description",
        "enhanced_description": "Gemini-enhanced technical video prompt",
        "video_concept": {
            "visual_style": "Professional commercial style",
            "scenes": ["Scene breakdown with timing"],
            "camera_movements": ["Specific camera techniques"],
            "lighting": "Professional lighting setup",
            "colors": "Color palette description",
            "audio_suggestions": "Audio/music recommendations"
        },
        "video_url": "https://generated-video-url.com/video.mp4",
        "duration_seconds": 4,
        "aspect_ratio": "16:9",
        "provider": "gemini_enhanced",
        "technical_specs": {
            "enhanced_by": "gemini-2.0-flash-exp",
            "scene_breakdown": ["Detailed scene descriptions"],
            "camera_movements": ["Professional camera techniques"],
            "lighting": "Technical lighting specifications"
        }
    }
    """
    try:
        # Validate input
        if not request.description.strip():
            raise HTTPException(
                status_code=400, 
                detail="Description cannot be empty"
            )
        
        # Validate duration
        if request.duration_seconds < 2 or request.duration_seconds > 10:
            raise HTTPException(
                status_code=400, 
                detail="Duration must be between 2 and 10 seconds"
            )
        
        # Validate aspect ratio
        valid_ratios = ["16:9", "9:16", "1:1"]
        if request.aspect_ratio not in valid_ratios:
            raise HTTPException(
                status_code=400, 
                detail=f"Aspect ratio must be one of: {', '.join(valid_ratios)}"
            )
        
        # Generate the video
        result = generate_video_from_description(
            description=request.description.strip(),
            duration_seconds=request.duration_seconds,
            aspect_ratio=request.aspect_ratio,
            trace_id=request.trace_id
        )
        
        if result.get("generation_status") == "error":
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Unknown video generation error")
            )
        
        # Return the generated video data
        return {
            "trace_id": result.get("trace_id"),
            "generation_status": result.get("generation_status"),
            "original_description": result.get("original_description"),
            "enhanced_description": result.get("enhanced_description"),
            "video_concept": result.get("video_concept", {}),
            "video_url": result.get("video_url"),
            "download_url": result.get("video_url"),
            "local_path": result.get("local_path"),
            "file_size": result.get("file_size"),
            "duration_seconds": result.get("duration_seconds"),
            "aspect_ratio": result.get("aspect_ratio"),
            "provider": result.get("provider", "gemini_enhanced"),
            "gemini_processing": result.get("gemini_processing"),
            "technical_specs": result.get("technical_specs", {}),
            "finish_reason": result.get("finish_reason")
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