# Ollama → Google Gemini API Migration Analysis

## Executive Summary
Complete migration of RAG chatbot from local Ollama (Microsoft Phi-2) to Google Gemini 2.5 Flash API while preserving entire retrieval architecture.

---

## Current Architecture

### Components
```
User Query
  ↓
Chat Endpoint (/api/v1/chat/message)
  ↓
RAG Chatbot Service
  ├─ Retriever: FAISS + SentenceTransformers (Embeddings)
  ├─ Knowledge Base: 8 agricultural Q&A pairs
  └─ LLM Generation: Ollama (phi model) ← BEING REPLACED
  ↓
Response with Sources
```

### Current Ollama Integration

**Location:** `backend/app/services/rag_chatbot.py`

**Ollama Usage Points:**
1. **Line 18:** `OLLAMA_BASE_URL` - Environment variable for server endpoint
2. **Line 19:** `OLLAMA_MODEL` - Model name (default: "phi")
3. **Line 48:** `self.ollama_available` - Availability flag
4. **Line 51:** `self._check_ollama()` - Connection check (line 144-158)
5. **Line 164:** `chat()` method calls `_generate_response()` with LLM fallback
6. **Line 237:** `_generate_response()` - Main LLM generation with Ollama
7. **Line 260:** `_call_ollama()` - Direct Ollama API call via httpx
8. **Line 266:** System prompt for farming expert persona
9. **Line 285:** Ollama API request payload with temperature, top_p, num_predict, etc.

**Environment Variables:**
- `OLLAMA_BASE_URL` → Default: `http://localhost:11434`
- `OLLAMA_MODEL` → Default: `phi`

**Model Details:**
- Microsoft Phi-2 (3B parameters, Q4_0 quantization)
- Local inference

**Httpx Usage:**
- Used for both Ollama availability check and API calls
- No dedicated Ollama SDK (just raw HTTP)

---

## What WILL Change

### 1. Remove Ollama
- ❌ Delete lines 17-19 (Ollama config)
- ❌ Delete `_check_ollama()` method (lines 144-158)
- ❌ Delete all Ollama availability checks
- ❌ Remove `self.ollama_available` flag

### 2. Add Gemini Integration
- ✅ Install: `google-generativeai`
- ✅ Create new service: `gemini_service.py`
- ✅ Initialize Gemini client from env var
- ✅ Implement generation with retry logic

### 3. Update RAG Flow
- Keep FAISS retrieval (lines 190-215)
- Keep keyword fallback search (lines 217-234)
- Replace `_call_ollama()` with `_call_gemini()`
- Preserve prompt template structure

---

## What WILL NOT Change

### Preserved Components
1. **Retrieval Pipeline:**
   - FAISS index creation and search
   - SentenceTransformers embeddings
   - Keyword fallback search
   - Retrieved document formatting

2. **Knowledge Base:**
   - All 8 Q&A entries remain
   - Crop categories and metadata
   - Knowledge base loading mechanism

3. **Prompt Templates:**
   - System prompt (farmer expert persona) → Adapted for Gemini
   - User prompt structure
   - Context injection from retrieved docs
   - Extra context from conversation (crop, disease, weather, etc.)

4. **Response Processing:**
   - `_clean_response()` post-processing
   - Response cutting at fake continuations
   - Source tracking
   - Chat session management in database

5. **Fallback Mechanisms:**
   - Template-based responses when no retrieval results
   - Static fallback response
   - Connection error handling

---

## Files to Modify

### Direct Changes
1. **`backend/app/services/rag_chatbot.py`**
   - Remove Ollama imports and config
   - Replace `_check_ollama()` with gemini initialization check
   - Replace `_call_ollama()` with `_call_gemini()`
   - Update docstrings

2. **`backend/app/core/config.py`**
   - Add `GEMINI_API_KEY` setting
   - Add `GEMINI_MODEL` setting (default: "gemini-2.5-flash")
   - Remove Ollama-related HuggingFace/LLM settings if unused

3. **`backend/requirements.txt`**
   - Add: `google-generativeai>=0.3.0`
   - Remove: None (no Ollama SDK was used)

### New Files
1. **`backend/app/services/gemini_service.py`**
   - Centralized Gemini client
   - Initialization with API key
   - Error handling and retries
   - Timeout handling

### Documentation
1. **`README.md`** - Update Ollama references to Gemini
2. **`.env.example`** - Add GEMINI_API_KEY

---

## Environment Configuration

### Remove
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi
```

### Add
```bash
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
```

---

## API Comparison

### Ollama API (Removed)
```python
POST http://localhost:11434/api/generate
{
    "model": "phi",
    "prompt": "...",
    "system": "...",
    "stream": False,
    "options": {
        "temperature": 0.5,
        "top_p": 0.8,
        "num_predict": 200,
        "repeat_penalty": 1.3
    }
}
```

### Gemini API (New)
```python
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents=[
        {"role": "user", "parts": [{"text": prompt}]}
    ],
    generation_config=genai.types.GenerationConfig(
        temperature=0.5,
        top_p=0.8,
        max_output_tokens=200
    ),
    system_instruction=system_prompt,
    safety_settings=[...]
)
```

---

## Prompt Template (Preserved with Minor Adjustments)

### System Prompt
```
You are Agrovee AI, a senior agronomist and plant pathologist with 20 years of field experience.
You work inside the Agrovee crop-health platform. You speak like a knowledgeable farming expert
who has personally dealt with every common crop disease.

YOUR VOICE:
- Confident and direct. You KNOW the answer — never hedge with 'I suggest you consult someone else'.
- Practical: give exact steps a farmer can do TODAY.
- Use bullet points for treatment steps.
- Keep answers 80-120 words. Be dense with useful info, no filler.

STRICT RULES:
1. NEVER say 'As an AI', 'As an Agrovee assistant', 'As a language model', or similar. You are a farming expert, period.
2. NEVER mention sources, references, citations, or '[Source]'. Just state facts directly.
3. NEVER say 'consult your local agronomist' or 'consult an expert' — YOU are the expert.
4. NEVER generate fake conversations, follow-up questions you answer yourself, puzzles, or scenarios.
5. Give ONE direct answer, then STOP.
6. Use emoji sparingly: 🌱 🌾 💧 🐛 ✅
```

### User Prompt
```
Agricultural knowledge:
{context_text}
{extra_context}
Farmer asks: {user_message}

Answer as a confident farming expert. Be specific and actionable. No source references. One answer, then stop.
```

---

## Testing Checklist

- [ ] Retrieval still works (FAISS + embeddings)
- [ ] Gemini API key loaded from environment
- [ ] Gemini generates responses using retrieved context
- [ ] Extra context injected (crop, disease, weather, etc.)
- [ ] Response post-processing works (clean_response)
- [ ] Fallback template responses work
- [ ] No Ollama references in code
- [ ] No Ollama in dependencies
- [ ] Chat endpoints functional
- [ ] Session management works
- [ ] Error handling for API failures
- [ ] Timeout handling for slow responses

---

## Status
- [ ] Create gemini_service.py
- [ ] Update rag_chatbot.py
- [ ] Update config.py
- [ ] Update requirements.txt
- [ ] Update README.md
- [ ] Test end-to-end
- [ ] Remove Ollama setup instructions

