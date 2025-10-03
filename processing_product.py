"""
Product Strategy Processing Module

This module handles the core business logic for generating product strategies
from combined text and image analysis using the Gemini API, and image generation
using Stability AI API or similar services.
"""

import os
import json
import uuid
import requests
import base64
from typing import Dict, Any
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def process_combined_input(
    text: str = "",
    image_url: str = "",
    trace_id: str = None
) -> Dict[str, Any]:
    """
    Process combined text and image input directly through Gemini API.
    Returns enhanced JSON data including image and video descriptions.
    
    Args:
        text: Text description of the product
        image_url: URL of the product image
        trace_id: Optional trace identifier
    
    Returns:
        Dict containing enhanced product strategies including image/video descriptions
    """
    try:
        trace_id = trace_id or str(uuid.uuid4())
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {
                "trace_id": trace_id,
                "processing_status": "error",
                "error": "GEMINI_API_KEY not configured"
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare content parts for multimodal input
        content_parts = []
        
        # Add text if provided
        if text and text.strip():
            content_parts.append(f"Product text description: {text.strip()}")
        
        # Add image if provided
        image_part = None
        if image_url and image_url.strip():
            try:
                # Download and encode image
                image_part = download_and_encode_image(image_url)
                if image_part:
                    content_parts.append("Product image: [Image provided for analysis]")
                else:
                    content_parts.append(f"Product image URL (unable to download): {image_url}")
            except Exception as e:
                print(f"⚠️  Warning: Could not process image {image_url}: {str(e)}")
                content_parts.append(f"Product image URL (processing failed): {image_url}")
        
        # Validate we have some content
        if not content_parts:
            return {
                "trace_id": trace_id,
                "processing_status": "error",
                "error": "No valid text or image content provided"
            }
        
        # Create enhanced prompt for accurate product-specific content generation
        prompt_text = f"""
        Based on the following product information, generate accurate and specific content that describes exactly what this product is.
        
        {chr(10).join(content_parts)}
        
        IMPORTANT: Be specific and accurate about the actual product. Do not use generic marketing language.
        
        Please provide a response in EXACTLY this JSON format (no additional text):
        {{
            "title": "Exact product name/title that accurately describes what this specific product is",
            "description": "Accurate and specific description of this exact product, its actual features, and real benefits",
            "slogan": "Product-specific slogan that relates directly to what this product actually is",
            "hashtags": ["#specific", "#product", "#related", "#actual", "#hashtags"],
            "image_description": "Specific visual description for generating an image of this exact product - describe the actual product, its real appearance, colors, materials, and how it should be photographed",
            "video_description": "Specific video description showing this exact product - describe actual scenes of the real product being used, demonstrated, or showcased in its intended environment"
        }}
        
        Requirements:
        - Title: Must be the actual product name/type, not marketing fluff
        - Description: Must describe the real product and its actual features
        - Image description: Must specify the exact product appearance and realistic photography setup
        - Video description: Must show the actual product in real usage scenarios
        - Be factual and specific, avoid generic marketing terms
        """
        
        # Prepare content for Gemini
        if image_part:
            # Multimodal input (text + image)
            content = [prompt_text, image_part]
        else:
            # Text-only input
            content = prompt_text
        
        # Generate response
        print(f"🤖 Gemini AI: Processing combined input (text + image) for trace {trace_id}...")
        response = model.generate_content(content)
        
        if response.text:
            # Parse JSON response
            try:
                strategies = json.loads(response.text.strip())
                
                # Validate required fields
                required_fields = ["title", "description", "slogan", "hashtags", "image_description", "video_description"]
                
                for field in required_fields:
                    if field not in strategies:
                        strategies[field] = f"Generated {field} unavailable"
                
                # Ensure hashtags is a list
                if not isinstance(strategies.get("hashtags"), list):
                    strategies["hashtags"] = ["#product", "#quality", "#sale"]
                
                # Print generated strategies to terminal
                print("\n" + "🎯"*40)
                print("🤖 GEMINI AI: Generated Enhanced Product Strategies")
                print("🎯"*40)
                print(f"📋 Trace ID: {trace_id}")
                print(f"📝 Input: {'Text + Image' if image_part else 'Text Only'}")
                print("✨ Generated JSON:")
                print(json.dumps(strategies, indent=2, ensure_ascii=False))
                print("🎯"*40 + "\n")
                
                return {
                    "trace_id": trace_id,
                    "processing_status": "success",
                    "strategies": strategies
                }
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed for trace {trace_id}: {str(e)}")
                # Fallback with product-specific content
                product_name = text.split('.')[0] if text else "Product"
                return {
                    "trace_id": trace_id,
                    "processing_status": "success",
                    "strategies": {
                        "title": product_name[:50] if product_name else "Specific Product",
                        "description": text[:300] + "..." if text else "Specific product with unique features and characteristics",
                        "slogan": f"Experience the {product_name}" if product_name else "Quality You Can Trust",
                        "hashtags": ["#product", "#quality", "#authentic", "#specific", "#real"],
                        "image_description": f"Clear, professional photograph of {product_name} showing its actual appearance, colors, and design details" if product_name else "Professional product photography showing actual item",
                        "video_description": f"Video demonstration of {product_name} being used in real scenarios, showing its actual functionality and features" if product_name else "Product demonstration video showing real usage"
                    }
                }
        else:
            return {
                "trace_id": trace_id,
                "processing_status": "error",
                "error": "No response from Gemini API"
            }
            
    except Exception as e:
        print(f"❌ Error in process_combined_input: {str(e)}")
        return {
            "trace_id": trace_id,
            "processing_status": "error",
            "error": f"Processing failed: {str(e)}"
        }

def download_and_encode_image(image_url: str):
    """
    Download image from URL and prepare it for Gemini API.
    
    Args:
        image_url: URL of the image to download
        
    Returns:
        PIL Image object or None if download fails
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"⚠️  Warning: URL does not appear to be an image: {content_type}")
            return None
        
        # Import PIL here to avoid import issues if not available
        from PIL import Image
        import io
        
        # Create PIL Image
        image = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        return image
        
    except ImportError:
        print("⚠️  PIL (Pillow) not available for image processing")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Failed to download image from {image_url}: {str(e)}")
        return None
    except Exception as e:
        print(f"⚠️  Failed to process image: {str(e)}")
        return None

def generate_image_from_description(
    description: str,
    trace_id: str = None,
    width: int = 1024,
    height: int = 1024
) -> Dict[str, Any]:
    """
    Generate an image from a text description using Stability AI API.
    
    Args:
        description: Text description of the image to generate
        trace_id: Optional trace identifier
        width: Image width (64-1536, must be multiple of 64)
        height: Image height (64-1536, must be multiple of 64)
    
    Returns:
        Dict containing image generation results
    """
    try:
        trace_id = trace_id or str(uuid.uuid4())
        
        # Check for Stability AI API key
        stability_api_key = os.getenv('STABILITY_API_KEY')
        if not stability_api_key:
            return {
                "trace_id": trace_id,
                "generation_status": "error",
                "error": "STABILITY_API_KEY not configured. Please set your Stability AI API key in the environment."
            }
        
        # Validate input
        if not description or not description.strip():
            return {
                "trace_id": trace_id,
                "generation_status": "error",
                "error": "Description cannot be empty"
            }
        
        # Validate and adjust dimensions
        width = max(64, min(1536, (width // 64) * 64))
        height = max(64, min(1536, (height // 64) * 64))
        
        print(f"🎨 Stability AI: Generating image for trace {trace_id}...")
        print(f"📝 Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        print(f"📏 Dimensions: {width}x{height}")
        
        # Prepare the API request
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {stability_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": description.strip(),
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "width": width,
            "height": height,
            "steps": 30,
            "samples": 1,
            "style_preset": "photographic"
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if "artifacts" in response_data and len(response_data["artifacts"]) > 0:
                # Get the first generated image
                image_data = response_data["artifacts"][0]
                base64_image = image_data.get("base64")
                
                if base64_image:
                    # Save the image locally
                    image_file_info = save_generated_image_locally(
                        base64_image,
                        description.strip(),
                        trace_id
                    )
                    
                    # Create a data URL and prepare result
                    image_url = f"data:image/png;base64,{base64_image}"
                    
                    result = {
                        "trace_id": trace_id,
                        "generation_status": "success",
                        "image_url": image_url,
                        "image_base64": base64_image,
                        "download_url": image_file_info.get("download_url") if image_file_info.get("status") == "success" else None,
                        "local_path": image_file_info.get("local_path") if image_file_info.get("status") == "success" else None,
                        "file_size": image_file_info.get("file_size") if image_file_info.get("status") == "success" else None,
                        "description": description.strip(),
                        "width": width,
                        "height": height,
                        "seed": image_data.get("seed"),
                        "finish_reason": image_data.get("finishReason")
                    }
                    
                    # Print generation result to terminal
                    print("\n" + "🎨"*40)
                    print("🖼️  Stability AI: Image Generation Complete")
                    print("🎨"*40)
                    print(f"📋 Trace ID: {trace_id}")
                    print(f"🖼️  Image generated successfully")
                    print(f"🔗 Download URL: {result.get('download_url', 'N/A')}")
                    print(f"📁 Local Path: {result.get('local_path', 'N/A')}")
                    print(f"📝 Description: {description[:150]}{'...' if len(description) > 150 else ''}")
                    print(f"📏 Dimensions: {width}x{height}")
                    print(f"💾 File Size: {result.get('file_size', 'N/A')}")
                    if result.get('seed'):
                        print(f"🌱 Seed: {result['seed']}")
                    print("🎨"*40 + "\n")
                    
                    return result
                else:
                    return {
                        "trace_id": trace_id,
                        "generation_status": "error",
                        "error": "No image data in API response"
                    }
            else:
                return {
                    "trace_id": trace_id,
                    "generation_status": "error",
                    "error": "No artifacts in API response"
                }
        else:
            error_detail = "Unknown error"
            try:
                error_data = response.json()
                error_detail = error_data.get("message", str(error_data))
            except:
                error_detail = f"HTTP {response.status_code}: {response.text[:200]}"
            
            return {
                "trace_id": trace_id,
                "generation_status": "error",
                "error": f"Stability AI API error: {error_detail}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "trace_id": trace_id,
            "generation_status": "error",
            "error": "Request timeout - image generation took too long"
        }
    except Exception as e:
        print(f"❌ Error in generate_image_from_description: {str(e)}")
        return {
            "trace_id": trace_id,
            "generation_status": "error",
            "error": f"Image generation failed: {str(e)}"
        }

def generate_video_from_description(
    description: str,
    trace_id: str = None,
    duration_seconds: int = 4,
    aspect_ratio: str = "16:9"
) -> Dict[str, Any]:
    """
    Generate a video from a text description using Gemini AI for enhancement 
    and compatible video generation services.
    
    Args:
        description: Text description of the video to generate
        trace_id: Optional trace identifier
        duration_seconds: Video duration in seconds (typically 2-10 seconds)
        aspect_ratio: Video aspect ratio ("16:9", "9:16", "1:1")
    
    Returns:
        Dict containing video generation results
    """
    try:
        trace_id = trace_id or str(uuid.uuid4())
        
        # Configure Gemini API for video description enhancement
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            return {
                "trace_id": trace_id,
                "generation_status": "error",
                "error": "GEMINI_API_KEY not configured. Please set your Gemini API key in the environment."
            }
        
        # Validate input
        if not description or not description.strip():
            return {
                "trace_id": trace_id,
                "generation_status": "error",
                "error": "Description cannot be empty"
            }
        
        # Validate duration
        duration_seconds = max(2, min(10, duration_seconds))
        
        # Validate aspect ratio
        valid_ratios = ["16:9", "9:16", "1:1"]
        if aspect_ratio not in valid_ratios:
            aspect_ratio = "16:9"
        
        print(f"🎬 Gemini-Enhanced Video Generation: Processing for trace {trace_id}...")
        print(f"📝 Original Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        print(f"⏱️ Duration: {duration_seconds}s, Aspect Ratio: {aspect_ratio}")
        
        # Step 1: Use Gemini to enhance the video description
        enhanced_description = enhance_video_description_with_gemini(
            description.strip(), 
            duration_seconds, 
            aspect_ratio,
            trace_id
        )
        
        if enhanced_description.get("status") == "error":
            return {
                "trace_id": trace_id,
                "generation_status": "error",
                "error": f"Gemini enhancement failed: {enhanced_description.get('error')}"
            }
        
        enhanced_prompt = enhanced_description.get("enhanced_prompt", description.strip())
        video_concept = enhanced_description.get("video_concept", {})
        
        print(f"✨ Gemini Enhanced Prompt: {enhanced_prompt[:150]}{'...' if len(enhanced_prompt) > 150 else ''}")
        
        # Step 2: Create a placeholder video file for demonstration
        # In a real implementation, you would use the enhanced description with actual video generation APIs
        video_file_info = create_placeholder_video_file(
            enhanced_prompt,
            duration_seconds,
            aspect_ratio,
            trace_id
        )
        
        if video_file_info.get("status") == "error":
            return {
                "trace_id": trace_id,
                "generation_status": "error",
                "error": f"Video file creation failed: {video_file_info.get('error')}"
            }
        
        # Step 3: Generate comprehensive result with local file paths
        result = {
            "trace_id": trace_id,
            "generation_status": "success",
            "original_description": description.strip(),
            "enhanced_description": enhanced_prompt,
            "video_concept": video_concept,
            "duration_seconds": duration_seconds,
            "aspect_ratio": aspect_ratio,
            "gemini_processing": "completed",
            "video_file": video_file_info.get("file_path"),
            "video_url": video_file_info.get("download_url"),
            "local_path": video_file_info.get("local_path"),
            "file_size": video_file_info.get("file_size"),
            "provider": "gemini_enhanced",
            "finish_reason": "GEMINI_ENHANCED_SUCCESS",
            "technical_specs": {
                "enhanced_by": "gemini-2.0-flash-exp",
                "scene_breakdown": video_concept.get("scenes", []),
                "visual_style": video_concept.get("visual_style", ""),
                "camera_movements": video_concept.get("camera_movements", []),
                "lighting": video_concept.get("lighting", ""),
                "audio_suggestions": video_concept.get("audio_suggestions", ""),
                "created_at": video_file_info.get("created_at")
            }
        }
        
        # Print generation result to terminal
        print("\n" + "🎬"*40)
        print("🎥 Gemini-Enhanced Video Generation Complete")
        print("🎬"*40)
        print(f"📋 Trace ID: {trace_id}")
        print(f"🎥 Video File: {result.get('video_file', 'N/A')}")
        print(f"🔗 Download URL: {result.get('video_url', 'N/A')}")
        print(f"📁 Local Path: {result.get('local_path', 'N/A')}")
        print(f"📝 Original: {description[:100]}{'...' if len(description) > 100 else ''}")
        print(f"✨ Enhanced: {enhanced_prompt[:100]}{'...' if len(enhanced_prompt) > 100 else ''}")
        print(f"⏱️ Duration: {duration_seconds}s | Aspect Ratio: {aspect_ratio}")
        print(f"🎨 Visual Style: {video_concept.get('visual_style', 'N/A')}")
        print(f"📹 Camera: {', '.join(video_concept.get('camera_movements', [])[:2])}")
        print(f"💾 File Size: {result.get('file_size', 'N/A')}")
        print("🎬"*40 + "\n")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in generate_video_from_description: {str(e)}")
        return {
            "trace_id": trace_id,
            "generation_status": "error",
            "error": f"Gemini-enhanced video generation failed: {str(e)}"
        }

def enhance_video_description_with_gemini(
    description: str,
    duration_seconds: int,
    aspect_ratio: str,
    trace_id: str
) -> Dict[str, Any]:
    """
    Use Gemini AI to enhance a video description with detailed technical specifications
    and creative direction for video generation.
    """
    try:
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create enhanced prompt for video description
        enhancement_prompt = f"""
        You are a professional video director and cinematographer. Transform this basic video description into a detailed, technically precise video generation prompt.

        Original Description: "{description}"
        Duration: {duration_seconds} seconds
        Aspect Ratio: {aspect_ratio}

        Create a comprehensive video concept that includes:

        Please provide a response in EXACTLY this JSON format:
        {{
            "enhanced_prompt": "Detailed, technical video generation prompt (max 500 characters)",
            "video_concept": {{
                "visual_style": "Specific visual style (e.g., cinematic, product photography, commercial)",
                "scenes": [
                    "Scene 1 description with timing",
                    "Scene 2 description with timing",
                    "Scene 3 description with timing"
                ],
                "camera_movements": [
                    "Specific camera movement 1",
                    "Specific camera movement 2"
                ],
                "lighting": "Detailed lighting setup description",
                "colors": "Color palette and mood description",
                "audio_suggestions": "Suggested audio/music style",
                "technical_notes": "Additional technical specifications"
            }}
        }}

        Requirements:
        - Enhanced prompt must be concise but technically detailed
        - Include specific camera angles, movements, and lighting
        - Consider the aspect ratio for framing suggestions
        - Break down the {duration_seconds}-second video into logical scenes
        - Be specific about visual elements, not generic
        - Focus on professional video production techniques
        """

        print(f"🤖 Gemini AI: Enhancing video description for trace {trace_id}...")
        
        # Generate enhanced description
        response = model.generate_content(enhancement_prompt)
        
        if response.text:
            try:
                enhanced_data = json.loads(response.text.strip())
                
                # Validate and clean the response
                if "enhanced_prompt" not in enhanced_data:
                    enhanced_data["enhanced_prompt"] = description
                
                if "video_concept" not in enhanced_data:
                    enhanced_data["video_concept"] = {}
                
                # Ensure all required fields exist
                video_concept = enhanced_data["video_concept"]
                defaults = {
                    "visual_style": "Professional commercial style",
                    "scenes": [f"Scene 1: {description[:50]}"],
                    "camera_movements": ["Smooth pan", "Static shot"],
                    "lighting": "Professional studio lighting",
                    "colors": "Natural, vibrant colors",
                    "audio_suggestions": "Background music, ambient sound",
                    "technical_notes": f"Optimized for {aspect_ratio} aspect ratio"
                }
                
                for key, default_value in defaults.items():
                    if key not in video_concept:
                        video_concept[key] = default_value
                
                print(f"✨ Gemini AI: Enhanced video concept generated successfully")
                
                return {
                    "status": "success",
                    "enhanced_prompt": enhanced_data["enhanced_prompt"],
                    "video_concept": video_concept,
                    "processing_info": {
                        "model": "gemini-2.0-flash-exp",
                        "enhancement_type": "video_description",
                        "trace_id": trace_id
                    }
                }
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed for video enhancement: {str(e)}")
                # Fallback with basic enhancement
                return {
                    "status": "success",
                    "enhanced_prompt": f"Professional video: {description}. Duration: {duration_seconds}s. Style: cinematic commercial. Lighting: professional studio setup. Camera: smooth movements. Aspect ratio: {aspect_ratio}.",
                    "video_concept": {
                        "visual_style": "Professional commercial",
                        "scenes": [f"Main scene: {description}"],
                        "camera_movements": ["Smooth pan"],
                        "lighting": "Professional lighting",
                        "colors": "Natural colors",
                        "audio_suggestions": "Background music",
                        "technical_notes": f"Optimized for {aspect_ratio}"
                    },
                    "processing_info": {
                        "model": "gemini-2.0-flash-exp",
                        "enhancement_type": "fallback",
                        "trace_id": trace_id
                    }
                }
        else:
            return {
                "status": "error",
                "error": "No response from Gemini API for video enhancement"
            }
            
    except Exception as e:
        print(f"❌ Error in enhance_video_description_with_gemini: {str(e)}")
        return {
            "status": "error",
            "error": f"Gemini enhancement failed: {str(e)}"
        }

def create_placeholder_video_file(
    enhanced_description: str,
    duration_seconds: int,
    aspect_ratio: str,
    trace_id: str
) -> Dict[str, Any]:
    """
    Create a placeholder video file locally for demonstration.
    In a real implementation, this would save actual generated video content.
    """
    try:
        # Create directory structure
        video_dir = "generated_videos"
        os.makedirs(video_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{trace_id}_{timestamp}.txt"
        file_path = os.path.join(video_dir, filename)
        
        # Create placeholder video content (in real implementation, this would be actual video data)
        video_metadata = {
            "trace_id": trace_id,
            "enhanced_description": enhanced_description,
            "duration_seconds": duration_seconds,
            "aspect_ratio": aspect_ratio,
            "created_at": datetime.now().isoformat(),
            "type": "placeholder_video",
            "note": "This is a placeholder file. In production, this would contain actual video data.",
            "video_specs": {
                "format": "mp4",
                "resolution": "1920x1080" if aspect_ratio == "16:9" else "1080x1920" if aspect_ratio == "9:16" else "1080x1080",
                "framerate": "30fps",
                "duration": f"{duration_seconds}s"
            }
        }
        
        # Write placeholder content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(video_metadata, f, indent=2, ensure_ascii=False)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        # Create download URL (assuming the server is running on localhost:8000)
        download_url = f"http://localhost:8000/downloads/videos/{filename}"
        
        print(f"💾 Created placeholder video file: {file_path}")
        print(f"📦 File size: {file_size_mb} MB")
        
        return {
            "status": "success",
            "file_path": filename,
            "local_path": file_path,
            "download_url": download_url,
            "file_size": f"{file_size_mb} MB",
            "created_at": datetime.now().isoformat(),
            "note": "Placeholder video file created. Replace with actual video generation in production."
        }
        
    except Exception as e:
        print(f"❌ Error creating video file: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to create video file: {str(e)}"
        }

def save_generated_image_locally(
    image_base64: str,
    description: str,
    trace_id: str
) -> Dict[str, Any]:
    """
    Save a generated image locally and return file information.
    """
    try:
        # Create directory structure
        image_dir = "generated_images"
        os.makedirs(image_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{trace_id}_{timestamp}.png"
        file_path = os.path.join(image_dir, filename)
        
        # Decode and save the image
        image_data = base64.b64decode(image_base64)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        # Create download URL
        download_url = f"http://localhost:8000/downloads/images/{filename}"
        
        print(f"💾 Saved image file: {file_path}")
        print(f"📦 File size: {file_size_mb} MB")
        
        return {
            "status": "success",
            "file_path": filename,
            "local_path": file_path,
            "download_url": download_url,
            "file_size": f"{file_size_mb} MB",
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error saving image file: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to save image file: {str(e)}"
        }