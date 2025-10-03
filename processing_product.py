"""
Product Strategy Processing Module

This module handles the core business logic for generating product strategies
from combined text and image analysis using the Gemini API.
"""

import os
import json
import uuid
import requests
from typing import Dict, Any
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