# AgriVisionTalk Backend API

FastAPI-based backend for multimodal AI crop health monitoring system.

## 🚀 Features

- ✅ **User Authentication**: JWT-based auth with access & refresh tokens
- ✅ **Database**: PostgreSQL with SQLAlchemy ORM
- ✅ **Diagnosis API**: Image upload and disease detection
- ✅ **Chat System**: RAG-powered agricultural chatbot
- ✅ **User Management**: Profile, statistics, history
- 🔄 **AI Integration**: Ready for vision model, multimodal fusion, decision engine
- 📚 **Auto Documentation**: OpenAPI/Swagger at `/api/docs`

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── api/                    # API endpoints
│   │   └── v1/
│   │       ├── api.py          # Router aggregator
│   │       └── endpoints/
│   │           ├── auth.py     # Authentication
│   │           ├── users.py    # User management
│   │           ├── diagnosis.py # Image diagnosis
│   │           └── chat.py     # RAG chatbot
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Settings
│   │   └── security.py         # JWT & password hashing
│   ├── db/                     # Database
│   │   └── session.py          # DB connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── diagnosis.py
│   │   └── chat.py
│   └── schemas/                # Pydantic schemas
│       ├── user.py
│       ├── diagnosis.py
│       └── chat.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Setup & Installation

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+
- (Optional) CUDA-enabled GPU for AI inference

### 2. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Install PostgreSQL (macOS)
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb agrivision_db

# Create user
psql -d agrivision_db -c "CREATE USER agrivision WITH PASSWORD 'agrivision123';"
psql -d agrivision_db -c "GRANT ALL PRIVILEGES ON DATABASE agrivision_db TO agrivision;"
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

**Important**: Update these in `.env`:
- `SECRET_KEY`: Generate secure random string
- `WEATHER_API_KEY`: Get from [OpenWeatherMap](https://openweathermap.org/api)
- `DATABASE_URL`: Your PostgreSQL connection string

### 5. Run the Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📖 API Documentation

Access interactive API docs at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔑 API Endpoints

### Authentication
```
POST   /api/v1/auth/register     - Register new user
POST   /api/v1/auth/login        - Login & get JWT tokens
GET    /api/v1/auth/me           - Get current user
POST   /api/v1/auth/logout       - Logout
POST   /api/v1/auth/refresh      - Refresh access token
```

### Users
```
GET    /api/v1/users/profile     - Get user profile
PUT    /api/v1/users/profile     - Update profile
POST   /api/v1/users/change-password - Change password
GET    /api/v1/users/stats       - Get user statistics
DELETE /api/v1/users/account     - Deactivate account
```

### Diagnosis
```
POST   /api/v1/diagnosis/diagnose      - Upload image for diagnosis
GET    /api/v1/diagnosis/diagnose/{id} - Get diagnosis result
GET    /api/v1/diagnosis/history       - Get diagnosis history
GET    /api/v1/diagnosis/recent        - Get recent diagnoses
DELETE /api/v1/diagnosis/diagnose/{id} - Delete diagnosis
```

### Chat
```
POST   /api/v1/chat/message           - Send chat message
GET    /api/v1/chat/sessions          - Get chat sessions
GET    /api/v1/chat/sessions/{id}     - Get session with messages
DELETE /api/v1/chat/sessions/{id}     - Delete chat session
PUT    /api/v1/chat/sessions/{id}/title - Update session title
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📊 Database Models

### User
- Authentication (email, password)
- Profile (name, location, farm size)
- Role & status
- Timestamps

### Diagnosis
- Image & predictions
- Weather & environmental data
- Multimodal fusion results
- Recommendations
- Explainability (Grad-CAM, LIME)

### Chat (Session & Messages)
- Conversation management
- RAG context & sources
- Token tracking

## 🔐 Security

- JWT tokens with HS256 algorithm
- Bcrypt password hashing
- CORS protection
- File upload validation
- Rate limiting (TODO)

## 📝 Next Steps (Step 2)

The backend structure is complete. Next steps:
1. **AI Service Layer**: Integrate vision model, multimodal fusion, decision engine
2. **RAG Chatbot**: FAISS vector store, HuggingFace embeddings
3. **Weather Integration**: OpenWeatherMap API
4. **Background Tasks**: Celery/Redis for async processing
5. **Frontend**: Next.js 14 application

## 🤝 Contributing

This is a research project. Follow IEEE software engineering standards.

## 📄 License

MIT License
