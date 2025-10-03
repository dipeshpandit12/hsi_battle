# Text Processing Module

This module handles the processing and enhancement of raw text input from sellers describing their products. It cleans, enhances, and analyzes text to prepare it for product strategy generation.

## 🎯 Purpose

The text processing module receives unstructured product descriptions from users and:
1. Cleans and normalizes the text
2. Enhances readability and structure
3. Calculates confidence scores based on text quality
4. Forwards processed data to the product strategy engine

## 📁 Files

- `main.py` - Core text processing functions and logic

## 🔧 Main Functions

### `process_seller_text(text: str) -> Dict[str, Any]`

**Primary entry point** for text processing.

**Input:**
```python
text = "Long unstructured text about the product..."
```

**Output:**
```python
{
    "trace_id": "12345-abcd-6789",
    "confidence": 0.92,
    "processing_status": "success",
    "enhanced_brief": "Enhanced and cleaned product description.",
    "product_response": {...}
}
```

### `clean_and_enhance_text(text: str) -> str`

**Text Enhancement Features:**
- Removes extra whitespace and normalizes formatting
- Filters out problematic special characters
- Ensures proper sentence structure and capitalization
- Adds proper punctuation where missing

**Example:**
```python
# Input
"this is a great product    with amazing features!!!! it works well"

# Output
"This is a great product with amazing features. It works well."
```

### `calculate_text_confidence(text: str) -> float`

**Confidence Scoring Factors:**
- **Word Count**: Optimal range 10-100 words (+0.2 points)
- **Sentence Structure**: Multiple sentences boost confidence (+0.15 points)
- **Product Keywords**: Presence of product-related terms (+0.05 per keyword, max +0.15)
- **Base Confidence**: 0.5 starting point

**Product Keywords Detected:**
- product, item, sell, buy, price, feature, benefit, quality, brand

**Confidence Scale:** 0.0 (lowest) to 1.0 (highest)

### `forward_to_processing_product(data: Dict[str, Any]) -> Dict[str, Any]`

Forwards the processed text data to the product strategy generation endpoint.

**Data Structure Sent:**
```python
{
    "source": "text",
    "enhanced_brief": "Enhanced product description...",
    "visual_brief": "",
    "trace_id": "unique-request-id"
}
```

## 🚀 Usage Example

```python
from processing_text.main import process_seller_text

# Raw seller input
raw_text = "smartphone with good camera battery life long"

# Process the text
result = process_seller_text(raw_text)

print(f"Trace ID: {result['trace_id']}")
print(f"Confidence: {result['confidence']}")
print(f"Enhanced: {result['enhanced_brief']}")

# Output:
# Trace ID: 12345-abcd-6789
# Confidence: 0.75
# Enhanced: "Smartphone with good camera battery life long."
```

## 🔄 Integration Flow

```
User Input → clean_and_enhance_text() → calculate_text_confidence() → forward_to_processing_product() → Product Strategy Engine
```

## ⚠️ Error Handling

The module handles various error conditions:
- **Empty Text**: Returns confidence 0.0 with error status
- **Processing Errors**: Returns error status with descriptive message
- **Forwarding Failures**: Graceful fallback with error logging

## 📊 Quality Metrics

**High Quality Text (Confidence > 0.8):**
- 20-80 words
- 2+ complete sentences
- Contains 3+ product keywords
- Proper grammar and structure

**Medium Quality Text (Confidence 0.5-0.8):**
- 10-20 words or 80-100 words
- 1-2 sentences
- Contains 1-2 product keywords

**Low Quality Text (Confidence < 0.5):**
- Very short (<10 words) or very long (>100 words)
- Poor sentence structure
- No recognizable product keywords

## 🔧 Dependencies

- `uuid` - For generating unique trace IDs
- `re` - For text cleaning and pattern matching
- `requests` - For HTTP communication with product endpoint
- `json` - For data serialization
- `typing` - For type hints

---

**Author:** Dipesh Pandit  
**Module:** Text Processing  
**Version:** 1.0.0