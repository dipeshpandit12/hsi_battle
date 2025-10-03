# Product Strategy API

This project provides a backend system for processing product-related data from text or images, and then generating optimized product strategies, titles, descriptions, and creative prompts using the Gemini API.

---

## 🚀 Overview

The system consists of a series of endpoints that work together to analyze products and generate marketing strategies:

1. **`/processing-text`** – Analyze raw text input, enhance it for clarity, and forward to `/processing-product`
2. **`/processing-image`** – Analyze an image (via URL), detect product attributes using Gemini Vision, and forward a description to `/processing-product`
3. **`/processing-product`** – Merge inputs, call `getProductStrategies`, and return structured strategies. Dispatches image/video prompts downstream
4. **`/image-generation`** – Receives prompts for product imagery and (for now) simply echoes the image description
5. **`/video-generation`** – Receives prompts for product videos and (for now) simply echoes the video description

---

## ⚙️ API Endpoints

### 1. `/processing-text`

**Input:**
```json
{
  "text": "Long unstructured text about the product..."
}
```

**Process:**
- Clean & enhance user input
- Forward to `/processing-product` with improved brief

**Output Example:**
```json
{
  "trace_id": "12345",
  "confidence": 0.92
}
```

### 2. `/processing-image`

**Input:**
```json
{
  "image_url": "https://example.com/image.png"
}
```

**Process:**
- Download & validate image
- Use Gemini Vision to detect objects & attributes
- Produce clear visual_brief
- Forward to `/processing-product`

**Output Example:**
```json
{
  "trace_id": "12345",
  "warnings": []
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

```
User → /processing-text
           ↓
      Enhanced text → /processing-product
           ↓
   getProductStrategies (Gemini)
           ↓
   ┌───────────────┬───────────────┐
   │ Return summary│ Dispatch media│
   └───────────────┴───────────────┘
        ↓                   ↓
   Frontend UI        /image-generation
                      /video-generation
```

---

## 📄 Author

**Designed by Dipesh Pandit**
