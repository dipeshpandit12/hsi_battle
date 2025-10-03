# Image Processing Module

This module handles the analysis of product images using Google's Gemini Vision API. It downloads, validates, and analyzes images to extract detailed product information and attributes.

## 🎯 Purpose

The image processing module receives image URLs from sellers and:
1. Downloads and validates images from URLs
2. Analyzes products using Gemini Vision AI
3. Generates detailed visual descriptions
4. Forwards processed data to the product strategy engine

## 📁 Files

- `main.py` - Core image processing functions and Gemini Vision integration

## 🔧 Main Functions

### `processing_seller_image(image_url: str) -> Dict[str, Any]`

**Primary entry point** for image processing.

**Input:**
```python
image_url = "https://example.com/product-image.jpg"
```

**Output:**
```python
{
    "trace_id": "12345-abcd-6789",
    "warnings": ["Image resolution is quite low"],
    "processing_status": "success",
    "visual_brief": "Detailed AI-generated product description...",
    "product_response": {...}
}
```

### `is_valid_url(url: str) -> bool`

**URL Validation:**
- Checks for proper URL format
- Validates scheme (http/https) and domain
- Returns boolean indicating URL validity

### `download_and_validate_image(image_url: str) -> tuple[bytes, List[str]]`

**Image Download & Validation Features:**
- **Safe Download**: Uses browser-like headers to avoid blocking
- **Timeout Protection**: 30-second download timeout
- **Content Type Validation**: Ensures proper image MIME types
- **Image Format Validation**: Uses PIL to verify image integrity
- **Resolution Analysis**: Warns about very low/high resolution images

**Validation Checks:**
- ✅ Valid image format (JPEG, PNG, WebP, etc.)
- ✅ Readable by PIL library
- ⚠️ Resolution warnings (<100px or >4000px)
- ⚠️ Content-type validation

**Example Warnings:**
```python
[
    "Image resolution is quite low",
    "Unexpected content type: text/html",
    "Image validation failed: cannot identify image file"
]
```

### `analyze_image_with_gemini(image_data: bytes) -> str`

**Gemini Vision Analysis:**

Uses Google's Gemini-1.5-Flash model to analyze product images with a specialized prompt.

**Analysis Focus Areas:**
1. **Product Type & Category** - What kind of product is it?
2. **Key Features & Attributes** - Technical specifications and characteristics
3. **Visual Elements** - Colors, materials, design elements
4. **Brand Recognition** - Visible logos or brand indicators
5. **Quality Assessment** - Condition and quality indicators
6. **Unique Selling Points** - Notable characteristics for marketing

**Example Analysis Output:**
```
"This image shows a black wireless smartphone with a sleek modern design. 
The device features a large edge-to-edge display with minimal bezels and 
appears to have a premium metal and glass construction. The back panel 
shows a prominent triple-camera system arranged vertically, suggesting 
advanced photography capabilities. The overall design indicates this is 
a high-end flagship device with premium build quality."
```

### `forward_to_processing_product(data: Dict[str, Any]) -> Dict[str, Any]`

Forwards the processed image data to the product strategy generation endpoint.

**Data Structure Sent:**
```python
{
    "source": "image",
    "enhanced_brief": "",
    "visual_brief": "AI-generated product description from image...",
    "trace_id": "unique-request-id"
}
```

## 🚀 Usage Example

```python
from processing_image.main import processing_seller_image

# Product image URL
image_url = "https://example.com/smartphone.jpg"

# Process the image
result = processing_seller_image(image_url)

print(f"Trace ID: {result['trace_id']}")
print(f"Warnings: {result['warnings']}")
print(f"Visual Brief: {result['visual_brief']}")

# Output:
# Trace ID: 12345-abcd-6789
# Warnings: []
# Visual Brief: "Modern smartphone with advanced camera system..."
```

## 🔄 Integration Flow

```
Image URL → URL Validation → Image Download → PIL Validation → Gemini Vision Analysis → forward_to_processing_product() → Product Strategy Engine
```

## 🤖 Gemini Vision Configuration

**Model:** `gemini-1.5-flash`  
**API Key:** Configured via `GEMINI_API_KEY` environment variable

**Specialized Analysis Prompt:**
The module uses a carefully crafted prompt that instructs Gemini to focus on product-specific attributes that are useful for generating marketing strategies.

## ⚠️ Error Handling

The module handles various error conditions gracefully:

**URL Errors:**
- Invalid URL format
- Network timeouts (30s limit)
- HTTP errors (404, 403, etc.)

**Image Errors:**
- Corrupted image files
- Unsupported formats
- Missing content-type headers

**API Errors:**
- Missing Gemini API key
- API rate limits
- Gemini service errors

**Fallback Behavior:**
- Returns descriptive error messages
- Provides fallback descriptions when AI analysis fails
- Continues processing with warnings rather than failing completely

## 📊 Supported Image Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **WebP** (.webp)
- **GIF** (.gif)
- **BMP** (.bmp)
- **TIFF** (.tiff)

## 🔧 Dependencies

- `requests` - For downloading images from URLs
- `uuid` - For generating unique trace IDs
- `json` - For data serialization
- `os` - For environment variable access
- `urllib.parse` - For URL validation
- `base64` - For image encoding (if needed)
- `io.BytesIO` - For image stream handling
- `PIL (Pillow)` - For image validation and processing
- `google.generativeai` - For Gemini Vision API integration
- `python-dotenv` - For environment variable loading
- `typing` - For type hints

## 🌐 Environment Variables

```bash
# Required for Gemini Vision analysis
GEMINI_API_KEY=your_gemini_api_key_here
```

## 📈 Performance Considerations

- **Image Size**: Large images are processed without resizing (Gemini handles optimization)
- **Timeout**: 30-second download timeout prevents hanging requests
- **Memory**: Images are processed in memory using BytesIO streams
- **Rate Limits**: Gemini API has rate limits - consider implementing retry logic for production

## 🔒 Security Features

- **Safe Headers**: Uses browser-like User-Agent to avoid blocking
- **Content Validation**: Verifies content-type before processing
- **Error Sanitization**: Sanitizes error messages to prevent information leakage
- **URL Validation**: Prevents processing of malicious URLs

---

**Author:** Dipesh Pandit  
**Module:** Image Processing  
**Version:** 1.0.0