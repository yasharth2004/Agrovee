# Ollama → Gemini Migration: Implementation Guide

## Summary of Changes

This document details all code changes made to migrate from local Ollama (Microsoft Phi-2) to Google Gemini 2.5 Flash API for RAG chatbot text generation.

---

## Files Modified

### 1. **`backend/app/services/gemini_service.py`** (NEW)
**Purpose:** Centralized Gemini API service layer

**Key Components:**
- `GeminiService` class - Handles Gemini client initialization and API calls
- `is_available()` - Checks if API is properly configured
- `generate_content()` - Main method for text generation with:
  - Retry logic (3 attempts by default)
  - Exponential backoff for rate limiting
  - Timeout handling (60s default)
  - Safety settings for agricultural content
  - Error handling for transient failures

**Usage:**
```python
from app.services.gemini_service import get_gemini_service

service = get_gemini_service()
if service.is_available():
    response = service.generate_content(
        prompt="...",
        system_instruction="...",
        temperature=0.5,
        max_output_tokens=200
    )
```

---

### 2. **`backend/app/services/rag_chatbot.py`** (MODIFIED)
**Changes:**

#### Removed:
- Line 10: `import httpx` (no longer needed for Ollama API calls)
- Lines 17-19: Ollama configuration environment variables
- Lines 48: `self.ollama_available` attribute
- Lines 51: `self._check_ollama()` initialization call
- Lines 144-158: `_check_ollama()` method (entire)
- All Ollama-specific logic in `_generate_response()`
- `_call_ollama()` method (entire)

#### Added:
- Line 10: `from app.services.gemini_service import get_gemini_service`
- Line 49: `self.gemini_service = None` attribute
- Lines 52: `self._initialize_gemini()` initialization call
- Lines 144-158: New `_initialize_gemini()` method
- New `_call_gemini()` method replacing `_call_ollama()`

#### Updated:
- **Docstrings:** Changed "Ollama (phi)" to "Google Gemini API"
- **`chat()` method:** Removed Ollama availability re-check
- **`_generate_response()` method:** Changed Ollama logic to Gemini logic
- **`_generate_fallback_response()` method:** Uses Gemini instead of Ollama

**Key Differences:**
- **Ollama:** Local HTTP API at `localhost:11434`, synchronous requests
- **Gemini:** Cloud API via Google Generative AI SDK, with built-in retry/timeout logic

---

### 3. **`backend/app/core/config.py`** (MODIFIED)
**Changes:**

Added two new environment variables:
```python
GEMINI_API_KEY: Optional[str] = None
GEMINI_MODEL: str = "gemini-2.5-flash"
```

**Purpose:**
- `GEMINI_API_KEY`: API key from Google AI Studio (required)
- `GEMINI_MODEL`: Model selection (default: gemini-2.5-flash)

---

### 4. **`backend/requirements.txt`** (MODIFIED)
**Added:**
```
google-generativeai>=0.3.0
```

**Why:**
- Official Google SDK for Gemini API
- Provides client, models, types, and configuration classes
- Handles authentication and API communication

**Removed:**
- Nothing (Ollama wasn't in requirements.txt — raw `httpx` was used)

---

### 5. **`README.md`** (MODIFIED)
**Changes:**

1. **Feature descriptions:**
   - "Ollama (phi model)" → "Google Gemini 2.5 Flash API"

2. **Architecture diagram:**
   - "Ollama phi (3B)" → "Gemini 2.5 Flash API"
   - "Ollama (localhost:11434, phi)" → "Google Gemini API (Cloud)"

3. **Tech stack table:**
   - LLM: "Ollama phi" → "Google Gemini 2.5 Flash"
   - Dependencies: Added "Google Generative AI SDK"

4. **Setup instructions:**
   - **Removed:** Step 5 Ollama setup (brew install, ollama serve, ollama pull phi)
   - **Added:** Step 5 Gemini setup (get API key from Google AI Studio, set env var)

5. **Environment variables:**
   - Added `GEMINI_API_KEY` (required)
   - Added `GEMINI_MODEL` (optional, default: gemini-2.5-flash)

---

## What Remained Unchanged

### Preserved RAG Components
✅ **Retrieval Pipeline:**
- FAISS index creation and search (L190-215)
- SentenceTransformers embeddings (L129)
- Keyword fallback search (L217-234)

✅ **Knowledge Base:**
- All 8 agricultural Q&A entries (kb_001 to kb_008)
- Category and crop metadata
- Loading mechanism

✅ **Prompt Templates:**
- System prompt (farming expert persona) - adapted for Gemini
- User prompt structure
- Context injection from retrieved docs
- Extra context from conversation

✅ **Response Processing:**
- `_clean_response()` post-processing (L325-374)
- Response cutting at fake continuations
- Source tracking
- Chat session management

✅ **Fallback Mechanisms:**
- Template-based responses (L376-403)
- Static fallback (L405-436)
- Connection error handling

---

## Installation & Setup

### 1. Install Dependencies
```bash
cd backend
pip install --upgrade -r requirements.txt
```

Specifically, this installs:
```bash
pip install google-generativeai>=0.3.0
```

### 2. Get Gemini API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key

### 3. Set Environment Variable

**Option A: Direct Environment Variable**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

**Option B: `.env` File** (recommended)
```bash
cd backend
cat > .env << EOF
# Existing variables...
SECRET_KEY=your-secret-key-change-in-production-min32chars!

# NEW: Google Gemini Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Other variables...
WEATHER_API_KEY=your-weather-api-key
EOF
```

### 4. Restart Backend
```bash
cd backend && python -m uvicorn app.main:app --reload
```

Or if using the shell script:
```bash
cd backend && ./start.sh
```

---

## Testing the Migration

### 1. Unit Test: Verify Service Initialization
```python
from app.services.gemini_service import get_gemini_service

service = get_gemini_service()
assert service.is_available() == True, "Gemini service not available - check API key"
print("✓ Gemini service initialized")
```

### 2. Functional Test: Chat Endpoint
```bash
# Create a chat session with a question
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "How do I prevent early blight in tomatoes?"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "session_id": 1,
  "role": "assistant",
  "content": "Early blight is best prevented by: 1) Crop rotation for 3-4 years, 2) Remove infected debris immediately, 3) Use disease-resistant tomato varieties, 4) Apply mulch to prevent soil splash, 5) Avoid overhead watering - water at base only, 6) Ensure spacing for air circulation, 7) Apply fungicides preventively during humidity...",
  "sources": "kb_001",
  "created_at": "2024-01-31T12:34:56.789Z"
}
```

### 3. Integration Test: Full RAG Flow
```bash
# Test with context (simulating diagnosis context)
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What should I do?",
    "context": {
      "crop": "tomato",
      "disease": "early blight",
      "confidence": 0.92,
      "weather": "high humidity, 25°C"
    }
  }'
```

### 4. Verification Checklist
- [ ] No Ollama processes running needed
- [ ] No local model files required
- [ ] `GEMINI_API_KEY` is set
- [ ] `google-generativeai` is installed
- [ ] Chat endpoint returns responses within 60s
- [ ] Retrieved documents are injected into prompt
- [ ] Context (crop, disease, weather) is included
- [ ] Responses follow farmer expert persona
- [ ] No "consult an agronomist" hedging
- [ ] Responses are 80-120 words
- [ ] Sessions are saved to database
- [ ] Sources are tracked correctly
- [ ] Fallback template works when Gemini unavailable
- [ ] No errors in logs about Ollama

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not set" Warning
**Solution:**
```bash
echo $GEMINI_API_KEY  # Verify it's set
export GEMINI_API_KEY="your-key-here"  # Set if missing
```

### Issue: "google-generativeai not installed"
**Solution:**
```bash
pip install google-generativeai>=0.3.0
```

### Issue: "API key invalid or quota exceeded"
**Solution:**
1. Verify key from https://aistudio.google.com/app/apikey
2. Check Google Cloud console for quota/billing issues
3. Ensure API is enabled for your project

### Issue: Timeout Errors (>60s response time)
**Solution:**
1. Gemini API is usually fast (<5s)
2. Check network connectivity
3. Try again (service has auto-retry logic)
4. Falls back to template responses if all retries fail

### Issue: Responses not using retrieved context
**Debug:**
```python
# Check what's being retrieved
response = chatbot_service.chat("your question")
print(response["retrieved_docs"])  # Should have 1-3 documents
```

---

## Migration Verification

### Pre-Migration vs Post-Migration

| Component | Before (Ollama) | After (Gemini) |
|-----------|-----------------|---|
| **LLM** | Microsoft Phi-2 (local) | Google Gemini 2.5 Flash (cloud) |
| **Model Size** | 3B parameters | Large (optimized) |
| **Inference Speed** | 5-30s (CPU dependent) | 1-5s (API) |
| **Setup** | Brew + `ollama pull phi` | Set env var |
| **Network** | Localhost only | Internet required |
| **Cost** | Free but runs locally | Free tier available |
| **Reliability** | Depends on local system | Google-managed |
| **Retry Logic** | Manual | Built-in (3 attempts) |
| **Timeout** | 120s | 60s (configurable) |

---

## Rollback Plan (if needed)

If you need to revert to Ollama:
1. Revert `rag_chatbot.py` from git history
2. Reinstall `httpx` if removed
3. Restart with Ollama running
4. No database changes needed (chatbot is stateless)

---

## Performance Notes

### Gemini vs Ollama
- **Gemini:** Faster, more capable, but requires internet
- **Ollama:** Slower, limited by local hardware, but private
- **Fallback:** Template responses work offline if Gemini unavailable

### Cost Considerations
- **Free tier:** 60 calls/minute (sufficient for single user)
- **Pro tier:** Unlimited (for production)
- Monitor via: https://console.cloud.google.com/

---

## Code Review Checklist

- [x] No hardcoded API keys (uses env var)
- [x] Proper error handling with logging
- [x] Retry logic for transient failures
- [x] Timeout handling
- [x] Graceful fallback when API unavailable
- [x] No breaking changes to chat endpoint
- [x] RAG retrieval pipeline unchanged
- [x] Prompt templates preserved
- [x] System instructions for expert persona intact
- [x] Response post-processing maintained
- [x] Session tracking preserved
- [x] Database compatibility maintained
- [x] Dependencies updated in requirements.txt
- [x] Config updated with Gemini settings
- [x] Documentation updated with setup steps
