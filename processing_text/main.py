import re
import uuid
import requests
import json
from typing import Dict, Any

def process_seller_text(text: str) -> Dict[str, Any]:
    """
    Process and enhance raw text input from seller.
    
    Args:
        text: Raw text input about the product
        
    Returns:
        Dict containing trace_id, confidence, and processing status
    """
    try:
        # Generate unique trace ID for this request
        trace_id = str(uuid.uuid4())
        
        # Clean and enhance the input text
        enhanced_brief = clean_and_enhance_text(text)
        
        # Calculate confidence based on text quality metrics
        confidence = calculate_text_confidence(enhanced_brief)
        
        # Forward to processing-product endpoint
        product_response = forward_to_processing_product({
            "source": "text",
            "enhanced_brief": enhanced_brief,
            "visual_brief": "",
            "trace_id": trace_id
        })
        
        return {
            "trace_id": trace_id,
            "confidence": confidence,
            "processing_status": "success",
            "enhanced_brief": enhanced_brief,
            "product_response": product_response
        }
        
    except Exception as e:
        return {
            "trace_id": str(uuid.uuid4()),
            "confidence": 0.0,
            "processing_status": "error",
            "error": str(e)
        }

def clean_and_enhance_text(text: str) -> str:
    """
    Clean and enhance raw text input for better processing.
    
    Args:
        text: Raw text input
        
    Returns:
        Enhanced and cleaned text
    """
    # Remove extra whitespace and normalize text
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere with processing
    cleaned = re.sub(r'[^\w\s\-\.\,\!\?\:\;]', '', cleaned)
    
    # Ensure proper sentence structure
    sentences = cleaned.split('.')
    enhanced_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            # Capitalize first letter of each sentence
            sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            enhanced_sentences.append(sentence)
    
    enhanced_text = '. '.join(enhanced_sentences)
    
    # Add period at the end if missing
    if enhanced_text and not enhanced_text.endswith('.'):
        enhanced_text += '.'
    
    return enhanced_text

def calculate_text_confidence(text: str) -> float:
    """
    Calculate confidence score based on text quality metrics.
    
    Args:
        text: Enhanced text
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    if not text:
        return 0.0
    
    # Base confidence factors
    word_count = len(text.split())
    sentence_count = len([s for s in text.split('.') if s.strip()])
    
    # Calculate confidence based on various factors
    confidence = 0.5  # Base confidence
    
    # Word count factor (optimal range: 10-100 words)
    if 10 <= word_count <= 100:
        confidence += 0.2
    elif word_count > 5:
        confidence += 0.1
    
    # Sentence structure factor
    if sentence_count >= 2:
        confidence += 0.15
    elif sentence_count >= 1:
        confidence += 0.1
    
    # Product-related keywords boost
    product_keywords = ['product', 'item', 'sell', 'buy', 'price', 'feature', 'benefit', 'quality', 'brand']
    keyword_matches = sum(1 for keyword in product_keywords if keyword.lower() in text.lower())
    confidence += min(keyword_matches * 0.05, 0.15)
    
    return min(confidence, 1.0)

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