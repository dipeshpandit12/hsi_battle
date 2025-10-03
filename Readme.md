# Product Strategy API

This project provides a backend system for processing product-related data from text or images, and then generating optimized product strategies, titles, descriptions, and creative prompts using the Gemini API.

---

## 🚀 Overview

The system consists of a flexible series of endpoints that work together to analyze products and generate marketing strategies with multiple processing modes:

1. **`/processing-text`** – Analyze raw text input, enhance it for clarity, and forward to `/processing-product`
2. **`/processing-image`** – Analyze an image (via URL), detect product attributes using Gemini Vision, and forward a description to `/processing-product`
3. **`/processing-product`** – **Core engine** that merges inputs, calls `getProductStrategies`, and returns structured strategies
4. **`/processing-combined`** – **🆕 New!** Accept both text and image in a single request for streamlined processing
5. **`/image-generation`** – Receives prompts for product imagery and (for now) simply echoes the image description
6. **`/video-generation`** – Receives prompts for product videos and (for now) simply echoes the video description

### **🆕 Key Feature: Session-Based Correlation**
Use the `sessionId` parameter in both `/processing-text` and `/processing-image` endpoints to correlate inputs for the same product. When both endpoints receive the same `sessionId`, the system waits for both inputs before generating comprehensive strategies.

**Benefits:**
- **Multi-Modal Processing**: Combine text descriptions with visual analysis
- **Intelligent Waiting**: System waits up to 5 minutes for correlated input
- **Complete Context**: Generate better strategies with both text and image data
- **Flexible Workflow**: Support async input from different sources

---

## ⚙️ API Endpoints

### 1. `/processing-text`

**Input:**
```json
{
  "text": "Long unstructured text about the product...",
  "sessionId": "optional-session-id-for-correlation"
}
```

**Process:**
- Clean & enhance user input using advanced text processing
- Calculate confidence score based on content quality
- Forward to `/processing-product` with improved brief
- **New!** Support session-based correlation with image inputs

**Output Example:**
```json
{
  "trace_id": "12345",
  "confidence": 0.92,
  "session_id": "session-123",
  "message": "Processing complete or waiting for image input"
}
```

### 2. `/processing-image`

**Input:**
```json
{
  "image_url": "https://example.com/image.png",
  "sessionId": "optional-session-id-for-correlation"
}
```

**Process:**
- Download & validate image with comprehensive error handling
- Use Gemini Vision to detect objects, attributes, and product features
- Produce detailed visual_brief with marketing-focused analysis
- Forward to `/processing-product`
- **New!** Support session-based correlation with text inputs

**Output Example:**
```json
{
  "trace_id": "12345",
  "warnings": [],
  "session_id": "session-123",
  "message": "Processing complete or waiting for text input"
}
```

### 3. `/processing-product`

**Input:**
```json
{
  "source": "text" | "image",
  "enhanced_brief": "...",
  "visual_brief": "...",
  "trace_id": "12345"
}
```

**Process:**
- Merge briefs into a unified product context
- Call `getProductStrategies` → structured output from Gemini
- Validate JSON schema
- Return essential info to frontend
- Dispatch `image_description` → `/image-generation`
- Dispatch `video_description` → `/video-generation`

**Response Schema:**
```json
{
  "title": "Product title",
  "description": "Marketing-focused description",
  "slogan": "Catchy slogan",
  "hashtags": ["tag1", "tag2", "tag3"]
}
```

### 4. `/image-generation`

**Input:**
```json
{
  "image_description": "Prompt for product image"
}
```

**Output:** Echoes back the image description for now.

### 5. `/video-generation`

**Input:**
```json
{
  "video_description": "Prompt for product video"
}
```

**Output:** Echoes back the video description for now.

---

## 🔄 **Session-Based Correlation Workflow** 🆕

### **How It Works**
When you provide the same `sessionId` to both `/processing-text` and `/processing-image` endpoints, the system intelligently waits for both inputs before generating comprehensive product strategies.

### **Step-by-Step Example**

#### **Step 1: Send Text with SessionId**
```bash
curl -X POST http://localhost:8000/processing-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Premium wireless noise-cancelling headphones with 30-hour battery life",
    "sessionId": "user-session-123"
  }'
```

**Response:**
```json
{
  "trace_id": "abc-123",
  "confidence": 0.88,
  "session_id": "user-session-123",
  "message": "Waiting for image input to complete processing",
  "waiting_for": "image"
}
```

#### **Step 2: Send Image with Same SessionId**
```bash
curl -X POST http://localhost:8000/processing-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/headphones.jpg",
    "sessionId": "user-session-123"
  }'
```

**Response (Complete Strategies Generated):**
```json
{
  "trace_id": "def-456",
  "warnings": [],
  "session_id": "user-session-123",
  "message": "Processing completed with correlation",
  "strategies": {
    "title": "Premium Wireless Noise-Cancelling Headphones - 30Hr Battery Life",
    "description": "Immerse yourself in crystal-clear audio with these professional-grade wireless headphones. Featuring advanced active noise cancellation technology and an industry-leading 30-hour battery life, they're perfect for audiophiles, travelers, and professionals who demand exceptional sound quality and all-day comfort.",
    "slogan": "Silence the World, Amplify Your Sound",
    "hashtags": ["#WirelessHeadphones", "#NoiseCancelling", "#PremiumAudio", "#30HourBattery", "#ProfessionalGrade"]
  }
}
```

### **Alternative: Combined Processing**
For simultaneous input, use the `/processing-combined` endpoint:

```bash
curl -X POST http://localhost:8000/processing-combined \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Premium wireless noise-cancelling headphones with 30-hour battery life",
    "image_url": "https://example.com/headphones.jpg",
    "sessionId": "optional-session-id"
  }'
```

### **Session Management Features**
- **Automatic Cleanup**: Sessions expire after 5 minutes
- **Memory Efficient**: In-memory storage with intelligent cleanup
- **Error Handling**: Graceful handling of timeouts and failures
- **Flexible Order**: Text or image can be sent first
- **Unique Sessions**: Each sessionId creates isolated processing context

---

## 🧠 Core Function: `getProductStrategies`

This internal function powers the `/processing-product` endpoint.

**Input:** Unified product context (from text + image analysis)

**Output (strict JSON):**
```json
{
  "title": "Example title",
  "description": "Engaging description with key product details",
  "slogan": "Memorable slogan",
  "hashtags": ["#keyword1", "#keyword2"],
  "image_description": "Prompt for AI image generation",
  "video_description": "Prompt for AI video generation"
}
```

---

## 🔑 Key Features

- **Multi-source input:** Supports both text and image analysis
- **Schema-constrained generation:** Ensures predictable structured output
- **Async-ready:** Image/video generation can be offloaded to workers or queues
- **Traceability:** Each request carries a `trace_id` for logging and debugging
- **Extensible:** Future-proof for real image/video generation and marketplace integrations

---

## 📌 Next Steps

- [ ] Implement queue system for image/video generation
- [ ] Add JSON schema validation for Gemini outputs
- [ ] Integrate content safety filters for images and text
- [ ] Expand channel-specific strategies (Amazon, eBay, TikTok, etc.)

---

## 🏗️ System Flow

### **Traditional Flow (No Session)**
```
User → /processing-text → /processing-product → Strategies
User → /processing-image → /processing-product → Strategies
```

### **🆕 Session-Based Correlation Flow**
```
User → /processing-text (sessionId) → Wait for correlation
User → /processing-image (sessionId) → Merge data → /processing-product → Enhanced Strategies
```

### **Combined Processing Flow**
```
User → /processing-combined → Internal processing → /processing-product → Strategies
```

### **Detailed Data Flow**
```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTIONS                      │
├─────────────────────────────────────────────────────────────┤
│  /processing-text  │  /processing-image  │ /processing-     │
│  (with sessionId)  │  (with sessionId)   │  combined        │
└──────────┬─────────┴──────────┬──────────┴─────────┬────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                SESSION CORRELATION LOGIC                   │
├─────────────────────────────────────────────────────────────┤
│  • Wait for both inputs (up to 5 minutes)                  │
│  • Merge text + visual briefs                              │
│  • Generate unified product context                        │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                 /processing-product                         │
│              (CORE STRATEGY ENGINE)                         │
├─────────────────────────────────────────────────────────────┤
│  • Gemini AI strategy generation                           │
│  • JSON validation & quality checks                        │
│  • Marketing-focused output optimization                   │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ENHANCED OUTPUT                         │
├─────────────────────────────────────────────────────────────┤
│  • SEO-optimized titles                                    │
│  • Comprehensive descriptions                              │
│  • Memorable slogans                                       │
│  • Trending hashtags                                       │
│  • Future: Image/video generation prompts                  │
└─────────────────────────────────────────────────────────────┘
```

---

## � **Quick Start Guide**

### **Environment Setup**
```bash
# Required environment variable
export GEMINI_API_KEY="your_gemini_api_key_here"

# Start the server
python3 main.py
```

### **Testing the SessionId Feature**

#### **Option 1: Session Correlation (Recommended for separated inputs)**
```bash
# Step 1: Send text with sessionId
curl -X POST http://localhost:8000/processing-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "High-quality smartphone with excellent camera and battery",
    "sessionId": "demo-session-001"
  }'

# Step 2: Send image with same sessionId (completes processing)
curl -X POST http://localhost:8000/processing-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/phone.jpg",
    "sessionId": "demo-session-001"
  }'
```

#### **Option 2: Combined Processing (For simultaneous inputs)**
```bash
curl -X POST http://localhost:8000/processing-combined \
  -H "Content-Type: application/json" \
  -d '{
    "text": "High-quality smartphone with excellent camera and battery",
    "image_url": "https://example.com/phone.jpg"
  }'
```

#### **Option 3: Individual Processing (No correlation)**
```bash
# Process text only
curl -X POST http://localhost:8000/processing-text \
  -H "Content-Type: application/json" \
  -d '{"text": "High-quality smartphone description"}'

# Process image only  
curl -X POST http://localhost:8000/processing-image \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/phone.jpg"}'
```

### **🔧 SessionId Best Practices**
- **Use Unique IDs**: Generate unique sessionId for each product (e.g., `user-123-product-456`)
- **Timeout Awareness**: Sessions expire after 5 minutes
- **Error Handling**: Always check response status and handle correlation timeouts
- **Order Independence**: Text or image can be sent first in any order

---

## �📄 Author & Credits

**Designed and Developed by:** Dipesh Pandit  
**AI Integration:** Google Gemini 2.5 Flash  
**Framework:** FastAPI with Python 3.11+  
**Version:** 2.0.0 (Updated with Session-Based Correlation)

---

## 📞 Support & Documentation

For detailed module documentation, see:
- `processing_text/README.md` - Text processing with sessionId support
- `processing_image/README.md` - Image analysis with sessionId support  
- `processing_product.py` - Core strategy generation and session management

For issues and feature requests, please refer to the project repository.
