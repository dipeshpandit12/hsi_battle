import requests
import uuid
import json
import os
from typing import Dict, Any, List
from urllib.parse import urlparse
import base64
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def processing_seller_image(image_url: str) -> Dict[str, Any]:
    """
    Process image URL and analyze using Gemini Vision.
    
    Args:
        image_url: URL of the image to process
        
    Returns:
        Dict containing trace_id, warnings, and processing status
    """
    try:
        # Generate unique trace ID for this request
        trace_id = str(uuid.uuid4())
        warnings = []
        
        # Validate image URL
        if not image_url:
            return {
                "trace_id": trace_id,
                "warnings": ["No image URL provided"],
                "processing_status": "error",
                "error": "Image URL is required"
            }
        
        if not is_valid_url(str(image_url)):
            return {
                "trace_id": trace_id,
                "warnings": ["Invalid image URL format"],
                "processing_status": "error",
                "error": "Invalid URL format"
            }
        
        # Download and validate image
        image_data, download_warnings = download_and_validate_image(str(image_url))
        warnings.extend(download_warnings)
        
        if not image_data:
            return {
                "trace_id": trace_id,
                "warnings": warnings,
                "processing_status": "error",
                "error": "Failed to download or validate image"
            }
        
        # Analyze image with Gemini Vision
        visual_brief = analyze_image_with_gemini(image_data)
        
        if not visual_brief:
            warnings.append("Gemini Vision analysis failed, using fallback description")
            visual_brief = "Product image analysis unavailable"
        
        # Forward to processing-product endpoint
        product_response = forward_to_processing_product({
            "source": "image",
            "enhanced_brief": "",
            "visual_brief": visual_brief,
            "trace_id": trace_id
        })
        
        return {
            "trace_id": trace_id,
            "warnings": warnings,
            "processing_status": "success",
            "visual_brief": visual_brief,
            "product_response": product_response
        }
        
    except Exception as e:
        return {
            "trace_id": str(uuid.uuid4()),
            "warnings": ["Processing error occurred"],
            "processing_status": "error",
            "error": str(e)
        }

def is_valid_url(url: str) -> bool:
    """
    Validate if the provided string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def download_and_validate_image(image_url: str) -> tuple[bytes, List[str]]:
    """
    Download image from URL and validate it.
    
    Args:
        image_url: URL of the image to download
        
    Returns:
        Tuple of (image_bytes, warnings_list)
    """
    warnings = []
    
    try:
        # Set headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Download image with timeout
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            warnings.append(f"Unexpected content type: {content_type}")
        
        # Validate image using PIL
        try:
            image = Image.open(BytesIO(response.content))
            image.verify()  # Verify it's a valid image
            
            # Check image dimensions
            if hasattr(image, 'size'):
                width, height = image.size
                if width < 100 or height < 100:
                    warnings.append("Image resolution is quite low")
                elif width > 4000 or height > 4000:
                    warnings.append("Image resolution is very high")
            
        except Exception as e:
            warnings.append(f"Image validation failed: {str(e)}")
            return None, warnings
        
        return response.content, warnings
        
    except requests.exceptions.Timeout:
        warnings.append("Image download timed out")
        return None, warnings
    except requests.exceptions.RequestException as e:
        warnings.append(f"Failed to download image: {str(e)}")
        return None, warnings
    except Exception as e:
        warnings.append(f"Unexpected error during image download: {str(e)}")
        return None, warnings

def analyze_image_with_gemini(image_data: bytes) -> str:
    """
    Analyze image using Gemini Vision API.
    
    Args:
        image_data: Image data in bytes
        
    Returns:
        Visual description of the product in the image
    """
    try:
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            return None
        
        genai.configure(api_key=api_key)
        
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert image data to PIL Image for Gemini
        image = Image.open(BytesIO(image_data))
        
        # Create prompt for product analysis
        prompt = """
        Analyze this image and provide a detailed description of the product(s) visible. 
        Focus on:
        1. Product type and category
        2. Key features and attributes
        3. Colors, materials, and design elements
        4. Brand elements if visible
        5. Product condition and quality indicators
        6. Any unique selling points or notable characteristics
        
        Provide a clear, concise description that would help generate marketing strategies.
        """
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        if response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e:
        print(f"Error in Gemini Vision analysis: {str(e)}")
        return None

def forward_to_processing_product(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forward processed data to the processing-product endpoint.
    
    Args:
        data: Data to forward to processing-product
        
    Returns:
        Response from processing-product endpoint
    """
    try:
        # For now, return a mock response since processing-product endpoint doesn't exist yet
        # In production, this would make an HTTP request to the processing-product endpoint
        return {
            "status": "forwarded_to_processing_product",
            "data": data,
            "message": "Data successfully forwarded to processing-product endpoint"
        }
    except Exception as e:
        return {
            "status": "forward_error",
            "error": str(e)
        }