# 🚀 Agrovee Project - Quick Start Guide

## Environment Setup (Already Done ✅)

- ✅ Python 3.12 virtual environment created
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed  
- ✅ .env configuration file created

---

## ⚡ Running the Project

### Option 1: Run Both Servers Together (Recommended)

**Terminal 1 - Start Both Servers:**
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 (New) - Start Frontend:**
```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee
source venv/bin/activate
cd frontend
npm run dev
```

---

### Option 2: Run Backend Only

```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Access:** http://127.0.0.1:8000/api/docs

---

### Option 3: Run Frontend Only

```bash
cd /Users/yasharthkesarwani/Downloads/Agrovee/frontend
npm run dev
```

**Access:** http://localhost:3000

---

## 📋 All Available Commands

### Backend Commands

```bash
# Navigate to backend
cd /Users/yasharthkesarwani/Downloads/Agrovee/backend
source ../venv/bin/activate

# Development server (auto-reload)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Production server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
pytest

# Run specific test file
pytest tests/test_auth.py -v

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code with black
black app/

# Lint code with flake8
flake8 app/
```

### Frontend Commands

```bash
# Navigate to frontend
cd /Users/yasharthkesarwani/Downloads/Agrovee/frontend

# Development server (Turbo mode - faster hot reload)
npm run dev

# Production build
npm run build

# Start production server (after build)
npm start

# Run linting
npm run lint

# Run linting with fix
npm run lint -- --fix
```

### Full Stack Commands

```bash
# Navigate to project root
cd /Users/yasharthkesarwani/Downloads/Agrovee

# Install/update all dependencies
./setup-dev.sh

# Start both servers (requires 2 terminals)
# Terminal 1:
source venv/bin/activate && cd backend && python -m uvicorn app.main:app --reload

# Terminal 2:
cd frontend && npm run dev

# Or use the convenience script:
chmod +x start-full-stack.sh
./start-full-stack.sh
```

---

## 🌐 Access Points

After starting the servers, you can access:

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:3000 | Web application UI |
| **Backend API** | http://127.0.0.1:8000 | API endpoint |
| **API Docs (Swagger)** | http://127.0.0.1:8000/api/docs | Interactive API documentation |
| **API Docs (ReDoc)** | http://127.0.0.1:8000/api/redoc | Alternative API documentation |
| **Health Check** | http://127.0.0.1:8000/health | Backend health status |

---

## 🔧 Configuration

### Backend Configuration (.env)

The `.env` file is already configured with:

```ini
# Application
PROJECT_NAME=Agrovee API
ENVIRONMENT=development
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# Database (SQLite)
DATABASE_URL=sqlite:///./agrovee.db

# JWT
SECRET_KEY=dev-secret-key-change-in-production-min32-chars-random-string!

# Google Gemini (Optional - for AI chatbot)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

**To enable Gemini:**
1. Get API key: https://aistudio.google.com/app/apikey
2. Add to `.env`: `GEMINI_API_KEY=your-api-key-here`
3. Restart backend

### Frontend Configuration

Frontend is already configured to connect to `http://127.0.0.1:8000/api/v1`

---

## 📦 Project Structure

```
Agrovee/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py           # FastAPI app setup
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── core/             # Config & security
│   │   └── db/               # Database
│   ├── tests/                # Test files
│   ├── .env                  # Environment variables (development)
│   └── requirements*.txt     # Python dependencies
│
├── frontend/                  # Next.js application
│   ├── app/                  # Next.js pages & layouts
│   ├── components/           # React components
│   ├── lib/                  # Utilities & API client
│   ├── hooks/                # Custom React hooks
│   ├── package.json          # Node dependencies
│   └── tsconfig.json         # TypeScript config
│
├── venv/                     # Python virtual environment
├── .env.example              # Example configuration
└── start-full-stack.sh       # Startup script
```

---

## ✅ Verification Checklist

After starting servers, verify everything works:

### Backend Verification
```bash
# Check API is running
curl http://127.0.0.1:8000/health

# Check Swagger docs are accessible
open http://127.0.0.1:8000/api/docs

# Try a sample API call (after you have a token)
curl -X GET http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Frontend Verification
```bash
# Check frontend is running
open http://localhost:3000

# Verify hot reload works (make a change in any file, should refresh automatically)
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error: "ModuleNotFoundError: No module named 'app'"**
- Make sure you're in the `backend/` directory
- Activate venv: `source ../venv/bin/activate`

**Error: "Port 8000 already in use"**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
python -m uvicorn app.main:app --reload --port 8001
```

**Error: Missing dependencies**
```bash
# Reinstall all dependencies
pip install -r requirements-minimal.txt
```

### Frontend Won't Start

**Error: "Port 3000 already in use"**
```bash
# Use a different port
npm run dev -- -p 3001
```

**Error: Dependencies out of sync**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Database Issues

**Database locked or corrupted:**
```bash
# Remove the database (for development only!)
rm backend/agrovee.db

# It will recreate on next startup
```

---

## 📱 Features Available

### Authentication
- User registration & login
- JWT token-based authentication
- Password reset functionality
- User profile management

### Chat & RAG
- RAG chatbot with Gemini integration (optional)
- Retrieval-Augmented Generation
- Chat history persistence
- Knowledge base search

### Diagnosis
- Plant disease diagnosis (if models available)
- Image analysis
- Recommendation system

### Community
- Community posts & discussions
- Comments on posts
- User interactions

### Admin
- User management
- System monitoring
- Data management

---

## 🔐 Security Notes

**Development Only:**
- Default secret key is for development only
- Debug mode is enabled
- SQLite database is local only
- CORS is permissive for localhost

**Before Production:**
1. Change `SECRET_KEY` in `.env`
2. Set `DEBUG=False`
3. Change `ENVIRONMENT=production`
4. Use PostgreSQL instead of SQLite
5. Set proper `ALLOWED_ORIGINS`
6. Use HTTPS
7. Configure proper backup strategy

---

## 📚 Additional Resources

- **Backend README:** `backend/README.md`
- **Frontend README:** `frontend/README.md`
- **API Documentation:** `backend/API_DOCS.md`
- **Migration Guide:** `SETUP_GEMINI.md`
- **Architecture:** `MIGRATION_ANALYSIS.md`

---

## 🆘 Need Help?

### Common Tasks

**Restart everything:**
```bash
# Kill existing processes and start fresh
pkill -f "uvicorn"
pkill -f "next dev"
# Then start servers again
```

**View backend logs:**
```bash
tail -f backend/logs/app.log
```

**Reset development database:**
```bash
rm backend/agrovee.db
# Restart backend to recreate
```

**Update dependencies:**
```bash
# Backend
pip install --upgrade -r requirements-minimal.txt

# Frontend
npm update
```

---

## 📝 Notes

- Both servers support hot reload (auto-restart on file changes)
- API uses JWT tokens for authentication
- Frontend uses TypeScript and React
- Backend uses FastAPI with SQLAlchemy ORM
- Database is SQLite for development (PostgreSQL for production)

**Enjoy your Agrovee development! 🌾**
