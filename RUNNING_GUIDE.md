# 🎉 Agrovee Project is Running!

## ✅ Current Status

Both servers are **RUNNING AND READY TO USE**:

```
✓ Backend API: http://127.0.0.1:8000
✓ Frontend Web: http://localhost:3000
✓ Database: SQLite (local)
```

---

## 🌐 Access Your Application

### Frontend (User Interface)
```
URL: http://localhost:3000
Status: ✓ Running (Turbopack, Turbo dev mode)
Port: 3000
```

### Backend API
```
URL: http://127.0.0.1:8000
Status: ✓ Running (FastAPI/Uvicorn)
Port: 8000
```

### API Documentation (Interactive)
```
Swagger UI: http://127.0.0.1:8000/api/docs
ReDoc: http://127.0.0.1:8000/api/redoc
Health Check: http://127.0.0.1:8000/health
```

---

## 💻 Terminal Commands Reference

### Backend Commands

**Start Backend (from `/Users/yasharthkesarwani/Downloads/Agrovee/backend`):**

```bash
# With proper PYTHONPATH (recommended)
PYTHONPATH=/Users/yasharthkesarwani/Downloads/Agrovee/backend \
  /Users/yasharthkesarwani/Downloads/Agrovee/venv/bin/python \
  -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Or with reload enabled for development
PYTHONPATH=/Users/yasharthkesarwani/Downloads/Agrovee/backend \
  /Users/yasharthkesarwani/Downloads/Agrovee/venv/bin/python \
  -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Or in production (4 workers)
PYTHONPATH=/Users/yasharthkesarwani/Downloads/Agrovee/backend \
  /Users/yasharthkesarwani/Downloads/Agrovee/venv/bin/python \
  -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Run Tests:**
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/backend
source ../venv/bin/activate
pytest tests/
pytest tests/test_auth.py -v
pytest --cov=app
```

**Database:**
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/backend

# Initialize database
python scripts/init_db.py

# Seed demo data
python scripts/seed_demo_posts.py

# Remove database (fresh start)
rm agrovee.db
```

### Frontend Commands

**Start Frontend (from `/Users/yasharthkesarwani/Downloads/Agrovee/frontend`):**

```bash
# Turbo mode (fast reload)
npm run dev

# Production build
npm run build

# Start production build
npm start

# Lint code
npm run lint
```

---

## 📋 Complete Startup Commands (Quick Copy-Paste)

### Terminal 1: Start Backend
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/backend
PYTHONPATH=. /Users/yasharthkesarwani/Downloads/Agrovee/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Terminal 2: Start Frontend
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/frontend
npm run dev
```

---

## 🔌 API Endpoints (Examples)

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Register User
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test@123456"
  }'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=testuser&password=Test@123456'
```

### Chat Endpoint (Requires JWT Token)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "How do I prevent early blight?",
    "crop": "tomato"
  }'
```

---

## 📁 Project Structure

```
/Users/yasharthkesarwani/Downloads/Agrovee/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── api/               # API endpoints (/api/v1/...)
│   │   ├── services/          # Business logic (RAG, diagnosis, etc.)
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── core/              # Config and security
│   │   └── db/                # Database connection
│   ├── tests/                 # Unit and integration tests
│   ├── .env                   # Environment variables (development)
│   └── requirements*.txt      # Python dependencies
│
├── frontend/                  # Next.js React application
│   ├── app/                   # Next.js pages (/login, /dashboard, etc.)
│   ├── components/            # Reusable React components
│   ├── lib/                   # Utilities (API client, auth, etc.)
│   ├── hooks/                 # Custom React hooks
│   ├── package.json           # NPM dependencies
│   └── tsconfig.json          # TypeScript configuration
│
├── venv/                      # Python virtual environment
├── QUICK_START.md             # This file
└── SETUP_GEMINI.md            # Gemini API setup guide
```

---

## 🔐 Configuration

### Backend Environment (.env)
Located at: `/Users/yasharthkesarwani/Downloads/Agrovee/backend/.env`

**Key Variables:**
```ini
# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./agrovee.db

# Security
SECRET_KEY=dev-secret-key-change-in-production-min32-chars-random-string!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Optional: Google Gemini for AI Chat
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

**To Enable Gemini:**
1. Get API key: https://aistudio.google.com/app/apikey
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`
3. Restart backend

---

## 🧪 Testing

### Backend Tests
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/backend
source ../venv/bin/activate

# Run all tests
pytest

# Run specific test
pytest tests/test_auth.py -v

# With coverage report
pytest --cov=app --cov-report=html

# Run API test script
bash test_api.sh
```

### Frontend Tests (if needed)
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/frontend

# Lint
npm run lint
```

---

## 🚨 Troubleshooting

### Port Already in Use

**Backend port 8000 taken:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
PYTHONPATH=. /path/to/python -m uvicorn app.main:app --port 8001
```

**Frontend port 3000 taken:**
```bash
npm run dev -- -p 3001
```

### Module Not Found Error

**Solution:** Make sure PYTHONPATH is set when starting backend:
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/backend
PYTHONPATH=. /path/to/venv/python -m uvicorn app.main:app ...
```

### Dependencies Missing

**Backend:**
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee
source venv/bin/activate
cd backend
pip install -r requirements-minimal.txt
```

**Frontend:**
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/frontend
npm install --legacy-peer-deps
```

### Database Issues

**Reset database:**
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/backend
rm agrovee.db
# Restart backend to recreate
```

---

## 📱 Features

### Available Right Now
- ✅ **Authentication**: Register, login, JWT tokens
- ✅ **User Management**: Profile, settings
- ✅ **Chat**: Message history, session management
- ✅ **RAG Chatbot**: Knowledge base search + retrieval
- ✅ **Community**: Posts, comments, discussions
- ✅ **Admin Dashboard**: User and data management
- ✅ **API Documentation**: Swagger UI at /api/docs

### Optional Features
- ⏳ **Plant Diagnosis**: Requires AI models (see `p1/` folder)
- ⏳ **Gemini Integration**: Requires API key setup

---

## 📚 Documentation Files

- **[QUICK_START.md](QUICK_START.md)** - Setup and running guide
- **[SETUP_GEMINI.md](SETUP_GEMINI.md)** - Google Gemini integration
- **[backend/README.md](backend/README.md)** - Backend documentation
- **[frontend/README.md](frontend/README.md)** - Frontend documentation
- **[MIGRATION_ANALYSIS.md](MIGRATION_ANALYSIS.md)** - Architecture details

---

## 🔄 Development Workflow

### Making Changes

**Backend:**
1. Edit files in `backend/app/`
2. Changes auto-reload if using `--reload` flag
3. Check logs for errors
4. Test with curl or API docs

**Frontend:**
1. Edit files in `frontend/app/` or `frontend/components/`
2. Hot reload automatically on save
3. Check browser console for errors
4. Test in browser at http://localhost:3000

### Running Tests Before Commit

```bash
# Backend
cd backend
pytest

# Frontend
cd ../frontend
npm run lint
```

---

## 🎯 Next Steps

1. **Register a User**: Go to http://localhost:3000/register
2. **Login**: Use your credentials at http://localhost:3000/login
3. **Try Chat**: Go to /dashboard/chat and test the chatbot
4. **Explore API**: Visit http://127.0.0.1:8000/api/docs
5. **Check Community**: Browse /dashboard/community

---

## ⚡ Pro Tips

- Both servers support hot reload during development
- Check browser DevTools (F12) for frontend errors
- Check terminal output for backend logs
- API Docs are interactive - try requests from the UI
- Use `curl` for quick API testing
- Keep `.env` out of git (it's in `.gitignore`)

---

## 📞 Support

If you encounter issues:

1. **Check terminal output** - Backend logs are printed
2. **Check browser console** - Frontend errors appear (F12)
3. **Review documentation** - See files listed above
4. **Reset and restart** - Sometimes a clean restart helps
   ```bash
   pkill -f "uvicorn"
   pkill -f "node"
   # Then restart servers
   ```

---

## 🎊 You're All Set!

**Backend:** http://127.0.0.1:8000 ✓
**Frontend:** http://localhost:3000 ✓

Start building! 🚀

