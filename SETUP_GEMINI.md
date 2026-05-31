# Gemini RAG Chatbot: Complete Setup & Testing Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- Backend already set up and running

### 1. Install Dependencies
```bash
cd backend
pip install --upgrade google-generativeai>=0.3.0
pip install -r requirements.txt  # Or just the one package above
```

**Verify Installation:**
```bash
python -c "import google.generativeai; print('✓ google-generativeai installed')"
```

### 2. Get Gemini API Key (2 minutes)
1. Open: https://aistudio.google.com/app/apikey
2. Sign in with your Google account (free)
3. Click **"Create API key"**
4. Copy the key (looks like: `AQ.Ab8RN6KeH6...`)

**Create `.env` File:**
```bash
cd backend

# Create .env file with required variables
cat > .env << 'EOF'
# JWT Secret (change this!)
SECRET_KEY=your-secret-key-change-in-production-min32chars!

# Database
DATABASE_URL=sqlite:///./agrovee.db

# Weather (existing)
WEATHER_API_KEY=your-weather-api-key

# Google Gemini (NEW - paste your API key here)
GEMINI_API_KEY=your-api-key-here-paste-it-now
GEMINI_MODEL=gemini-2.5-flash

# Other settings
ENVIRONMENT=development
DEBUG=true
DEVICE=cpu
EOF
```

**Edit the file and paste your API key:**
```bash
nano .env  # Replace "your-api-key-here" with actual key
```

### 3. Restart Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see in logs:
```
✓ Gemini service initialized — using model 'gemini-2.5-flash'
```

### 4. Test the Chatbot (via Frontend or API)

**Via Frontend:**
1. Go to http://localhost:3000
2. Login with admin@agrovee.com / admin123
3. Navigate to **Chat** tab
4. Ask: "How do I prevent early blight in tomatoes?"
5. You should get a detailed, confident response from Gemini

**Via API (curl):**
```bash
# First, get a JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agrovee.com","password":"admin123"}' \
  | jq '.access_token' > token.txt

TOKEN=$(cat token.txt | tr -d '"')

# Now send a chat message
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "How do I prevent early blight in tomatoes?"
  }' | jq '.'
```

**Expected Response:**
```json
{
  "id": 1,
  "session_id": 1,
  "role": "assistant",
  "content": "Early blight is best prevented by: 1) Crop rotation for 3-4 years, 2) Remove infected debris immediately, 3) Use disease-resistant varieties, 4) Apply mulch to prevent soil splash, 5) Avoid overhead watering, 6) Ensure spacing for air circulation, 7) Apply preventive fungicides during humid periods.",
  "sources": "kb_001",
  "timestamp": "2024-01-31T12:34:56.789Z"
}
```

---

## Detailed Testing (20 minutes)

### Test 1: Basic Retrieval & Generation

**Question:** "What causes yellow leaves?"

**Expected Flow:**
1. Query retrieved from knowledge base (kb_002 - Yellow Leaves)
2. Gemini generates response using that context
3. Response mentions nitrogen, overwatering, iron deficiency

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"What causes yellow leaves?"}' | jq '.content'
```

---

### Test 2: Context-Aware Response

**Test with diagnosis context:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "How should I treat this?",
    "context": {
      "crop": "rice",
      "disease": "powdery mildew",
      "confidence": 0.87,
      "risk": "HIGH",
      "weather": "warm and humid"
    }
  }' | jq '.content'
```

**Verify:**
- Response mentions rice (crop context)
- Response mentions powdery mildew (disease context)
- Response is confident and actionable
- No "consult an expert" hedging

---

### Test 3: Fallback Responses

**Question with NO matching knowledge:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Tell me about growing dragon fruit"}' | jq '.content'
```

**Expected:** Gemini uses general knowledge to answer (no retrieved docs, but still helpful)

---

### Test 4: Session Persistence

**Create session 1:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"What is NPK ratio?"}' | jq '.session_id' > session_id.txt

SESSION=$(cat session_id.txt)

# Ask followup in same session
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"What about for tomatoes?\",\"session_id\":$SESSION}" | jq '.session_id'
```

**Verify:** Both messages have the same `session_id`

---

### Test 5: Message History

**Retrieve session:**
```bash
curl -X GET "http://localhost:8000/api/v1/chat/sessions" \
  -H "Authorization: Bearer $TOKEN" | jq '.sessions[0]'
```

**Verify:**
- Session title matches first question
- Session has multiple messages
- Messages are in correct order

---

### Test 6: Knowledge Base Coverage

Ask questions for each topic:

```bash
QUESTIONS=(
  "How to prevent early blight?"
  "What causes yellow leaves?"
  "When to apply fertilizer?"
  "How to manage powdery mildew?"
  "What is NPK ratio?"
  "Signs of overwatering?"
  "How to manage aphids?"
  "What is crop rotation?"
)

for q in "${QUESTIONS[@]}"; do
  echo "Testing: $q"
  curl -X POST http://localhost:8000/api/v1/chat/message \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"$q\"}" | jq '.sources'
  echo "---"
done
```

**Expected:** Each should have sources from knowledge base

---

## Verification Checklist

- [ ] `.env` file has valid `GEMINI_API_KEY`
- [ ] Backend starts without errors
- [ ] Logs show "✓ Gemini service initialized"
- [ ] Chat endpoint returns responses
- [ ] Responses include retrieved documents
- [ ] Context is used in responses
- [ ] Fallback works for unknowns
- [ ] Sessions persist across messages
- [ ] No "consult an expert" hedging in responses
- [ ] Responses are 80-120 words typically
- [ ] API calls complete within 60 seconds
- [ ] Database tracks all messages

---

## Troubleshooting

### Error: "GEMINI_API_KEY not set"

**Cause:** Environment variable not loaded

**Fix:**
```bash
# Check if set
echo $GEMINI_API_KEY

# If empty, reload shell
source ~/.bashrc  # or ~/.zshrc

# Or explicitly set
export GEMINI_API_KEY="your-key-here"

# Verify
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

### Error: "google-generativeai not installed"

**Fix:**
```bash
pip install google-generativeai>=0.3.0
```

### Error: "Invalid API key provided"

**Fix:**
1. Get new key from: https://aistudio.google.com/app/apikey
2. Verify key in `.env` (no spaces, full string)
3. Restart backend

### Error: "Timeout or no response"

**Cause:** Network issue or rate limit

**Fix:**
- Service has auto-retry (3 attempts)
- Falls back to template if all fail
- Check internet connection
- Try again in a few seconds

### Chat returns template response instead of Gemini

**Cause:** Gemini unavailable but retrieval worked

**Expected behavior:** This is correct! Shows fallback is working.

**To use Gemini again:** Check Gemini service logs:
```python
from app.services.gemini_service import get_gemini_service
service = get_gemini_service()
print(f"Available: {service.is_available()}")
```

---

## Performance Expectations

| Metric | Expected |
|--------|----------|
| **API Response Time** | 1-5 seconds |
| **Total Chat Response Time** | 2-7 seconds |
| **Retrieval Time** | <100ms |
| **Fallback Template Time** | <100ms |
| **First Request** | 3-10 seconds (API warmup) |
| **Concurrent Users** | ~100/minute (free tier limit) |

---

## API Keys Safety

### ⚠️ Security Notes

- **Never commit `.env` to git** — add to `.gitignore`
- **Never hardcode keys** in source code
- **Rotate keys regularly** in production
- **Monitor usage** at: https://console.cloud.google.com/
- **Set quota limits** to prevent surprise bills

**`.gitignore` check:**
```bash
cd backend
grep -i gemini .gitignore || echo ".env" >> .gitignore
```

---

## Advanced Configuration

### Use Different Model

```bash
# In .env
GEMINI_MODEL=gemini-pro  # Cheaper, smaller
# or
GEMINI_MODEL=gemini-2.5-flash  # Faster, recommended
```

### Adjust Generation Parameters

Edit `backend/app/services/gemini_service.py`, method `generate_content()`:

```python
# Temperature (0.0 = deterministic, 1.0 = random)
temperature=0.3,  # More consistent answers

# Top-p (nucleus sampling)
top_p=0.7,  # Less creative

# Max tokens (response length)
max_output_tokens=300,  # Longer responses

# Timeout
timeout=120,  # Longer wait time

# Retries
max_retries=5,  # More attempts
```

---

## Monitoring & Logging

### View Logs

```bash
# Real-time logs (if using --reload)
# Look for lines like:
# - "✓ Gemini service initialized"
# - "Sending request to Gemini API..."
# - "Gemini response received"
# - Any errors starting with "ERROR"

# Check if Gemini was called
grep -i "gemini" logs/app.log
```

### Monitor API Usage

1. Go to: https://console.cloud.google.com/
2. Select your project
3. View **"Generative Language API"** quotas
4. Check daily/monthly usage

---

## Next Steps

1. **Deploy to Production:**
   - Set `ENVIRONMENT=production` in `.env`
   - Set production secret key
   - Enable HTTPS
   - Monitor API quotas

2. **Expand Knowledge Base:**
   - Add more Q&A to `backend/app/services/rag_chatbot.py`
   - Retrain embeddings with `_initialize_embeddings()`

3. **Fine-tune Behavior:**
   - Adjust system prompt in `_call_gemini()`
   - Change temperature for more/less creativity
   - Modify max_output_tokens for response length

4. **Add Analytics:**
   - Track which questions are asked most
   - Monitor response quality
   - Improve knowledge base based on queries

---

## Support

### Resources
- **Gemini Docs:** https://ai.google.dev/tutorials
- **API Reference:** https://ai.google.dev/api
- **Free Tier:** https://ai.google.dev/pricing
- **Issues:** Check backend logs for detailed errors

### Common Errors Reference

| Error | Solution |
|-------|----------|
| `Invalid API key` | Get new key from AI Studio |
| `Rate limited` | Service auto-retries, try again |
| `Timeout` | Increase timeout in config |
| `No response` | Check internet, restart backend |
| `503 Service Unavailable` | Google API temporary issue, auto-retry will handle |
