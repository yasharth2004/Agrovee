# 🌾 Agrovee — AI-Powered Smart Farming Assistant

> A full-stack multimodal AI platform for **crop health monitoring, disease detection, and agricultural advisory**. Upload a photo of your crop and receive instant AI-powered disease identification, weather-contextualized risk analysis, actionable treatment plans, and conversational farming advice — all through a modern, responsive web interface with voice interaction support.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688)
![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black)
![React](https://img.shields.io/badge/React-19.2.3-61DAFB)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1.2-EE4C2C)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7.3-3178C6)
![Tests](https://img.shields.io/badge/Tests-87%20Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-81%25-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📑 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [AI Pipeline](#-ai-pipeline--5-service-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Voice Chat](#-voice-chat)
- [Supported Crops & Diseases](#-supported-crops--diseases-38-classes)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core AI Capabilities

| Feature | Description |
|---------|-------------|
| 🔬 **Crop Disease Detection** | Upload a leaf/plant image → ResNet50 deep learning model identifies crop type and disease across **38 classes** with confidence scores and top-5 predictions |
| 🌤️ **Weather-Aware Multimodal Fusion** | Combines computer vision predictions with **real-time weather data** (temperature, humidity, rainfall) and user-provided soil/season info for enhanced, context-aware accuracy |
| 💊 **Treatment Recommendations** | AI decision engine generates disease-specific treatment plans including chemical & organic options, fertilizer guidance (NPK ratios), irrigation schedules, cost estimates, and monitoring plans |
| 💬 **RAG Chatbot** | Retrieval-Augmented Generation chatbot powered by **Ollama (phi model)** with FAISS/keyword retrieval over an agricultural knowledge base — answers farming questions with cited sources |
| 🎙️ **Voice Chat** | Google Assistant–style full-screen voice overlay using the Web Speech API — speak questions, hear AI responses via text-to-speech, all hands-free |

### Platform Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Secure registration, login, refresh tokens, profile management with bcrypt password hashing |
| 📊 **Dashboard** | Personalized dashboard with diagnosis history, statistics, recent activity, and quick-action cards |
| 🌙 **Dark / Light Mode** | Full theme support via `next-themes` with smooth transitions across all pages |
| 📱 **Responsive Design** | Mobile-first responsive layouts built with Tailwind CSS and shadcn/ui components |
| ⚡ **Turbopack Dev** | Next.js Turbopack for blazing-fast development hot-reload |
| 🐳 **Docker Ready** | Dockerfile and docker-compose.yml for containerized deployment |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────┐
│          Client (Browser)            │
│  ┌────────────────────────────────┐  │
│  │  Next.js 16 + React 19        │  │
│  │  TypeScript · Tailwind CSS     │  │
│  │  shadcn/ui · Framer Motion     │  │
│  │  Voice Chat (Web Speech API)   │  │
│  └──────────────┬─────────────────┘  │
└─────────────────┼────────────────────┘
                  │ REST API (JSON)
                  │ JWT Bearer Auth
                  ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Backend (Python 3.12)            │
│  ┌─────────────────────────────────────────────────┐ │
│  │  API Layer (v1)                                 │ │
│  │  ├── /auth     — Register, Login, Refresh, Me   │ │
│  │  ├── /diagnosis — Upload, Diagnose, History     │ │
│  │  ├── /chat     — Messages, Sessions             │ │
│  │  └── /users    — Profile, Stats, Password       │ │
│  └───────────────────┬─────────────────────────────┘ │
│                      │                               │
│  ┌───────────────────▼─────────────────────────────┐ │
│  │  AI Service Layer (5 microservices)             │ │
│  │  ┌─────────────┐  ┌──────────────────────────┐ │ │
│  │  │ 1. Vision   │  │ 2. Weather Service       │ │ │
│  │  │  (ResNet50) │  │  (OpenWeatherMap +       │ │ │
│  │  │  38 classes │  │   Open-Meteo fallback)   │ │ │
│  │  └──────┬──────┘  └────────────┬─────────────┘ │ │
│  │         │                      │               │ │
│  │  ┌──────▼──────────────────────▼─────────────┐ │ │
│  │  │ 3. Multimodal Fusion                      │ │ │
│  │  │  Vision + Weather + Soil + Season → Risk  │ │ │
│  │  └──────────────────┬────────────────────────┘ │ │
│  │                     │                          │ │
│  │  ┌──────────────────▼────────────────────────┐ │ │
│  │  │ 4. Decision Engine                        │ │ │
│  │  │  Treatments · Fertilizer · Irrigation     │ │ │
│  │  │  Cost Estimates · Monitoring Schedules    │ │ │
│  │  └───────────────────────────────────────────┘ │ │
│  │                                                │ │
│  │  ┌───────────────────────────────────────────┐ │ │
│  │  │ 5. RAG Chatbot                            │ │ │
│  │  │  Ollama phi (3B) · FAISS · Keyword Search │ │ │
│  │  └───────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Data Layer                                    │  │
│  │  SQLite (agrovee.db) · SQLAlchemy ORM          │  │
│  │  Tables: users, diagnoses, chat_sessions,      │  │
│  │          chat_messages                          │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────┐
│  External Services                   │
│  ├── OpenWeatherMap API (weather)    │
│  ├── Open-Meteo API (fallback)       │
│  └── Ollama (localhost:11434, phi)   │
└──────────────────────────────────────┘
```

### Request Flow — Disease Diagnosis

```
User uploads image + (optional: soil_type, location, season)
    │
    ▼
1. Vision Model — ResNet50 inference → disease prediction + confidence + embeddings
    │
    ▼
2. Weather Service — fetches real-time weather from OpenWeatherMap for user's location
    │
    ▼
3. Multimodal Fusion — combines vision output + weather + soil + season
   → adjusted confidence, risk level (LOW/MEDIUM/HIGH/CRITICAL), risk factors
    │
    ▼
4. Decision Engine — generates treatment plan based on disease + risk + environment
   → immediate actions, chemical/organic treatments, fertilizer, irrigation, cost
    │
    ▼
5. Response returned with full diagnosis, recommendations, and weather context
```

---

## 🤖 AI Pipeline — 5-Service Architecture

### 1. Vision Model (`vision_model.py`)

| Attribute | Value |
|-----------|-------|
| **Architecture** | ResNet50 (pretrained, fine-tuned) |
| **Fallback** | MobileNetV2 (lighter, if ResNet unavailable) |
| **Classes** | 38 crop-disease combinations |
| **Training Data** | PlantVillage dataset (99.1% training accuracy) |
| **Model File** | `best_model.pth` (283 MB) |
| **Device** | Auto-detects CUDA/MPS/CPU |
| **Output** | Predicted disease, confidence %, crop type, top-5 predictions, 2048-dim embeddings |

### 2. Weather Service (`weather_service.py`)

| Attribute | Value |
|-----------|-------|
| **Primary API** | OpenWeatherMap (requires API key) |
| **Fallback API** | Open-Meteo (free, no key needed) |
| **Data Points** | Temperature, humidity, rainfall, wind speed, pressure, description |
| **Features** | Normalized (0–1) weather features for ML fusion |
| **Input** | City name or "lat,lon" coordinates |

### 3. Multimodal Fusion (`multimodal_fusion.py`)

| Attribute | Value |
|-----------|-------|
| **Approach** | Rule-based + heuristic hybrid |
| **Inputs** | Vision embeddings (2048-d) + weather (4-d) + soil type (one-hot) + season |
| **Adjustments** | Confidence boosted/reduced based on environmental disease-favorability |
| **Risk Levels** | LOW, MEDIUM, HIGH, CRITICAL |
| **Risk Factors** | "High humidity favorable for fungal disease", "Recent rainfall increases risk", etc. |

### 4. Decision Engine (`decision_engine.py`)

| Attribute | Value |
|-----------|-------|
| **Knowledge Base** | 20+ disease-specific treatment protocols |
| **Output Sections** | Immediate actions, chemical treatments, organic alternatives, fertilizer (NPK), irrigation, preventive measures, monitoring schedule, cost estimates |
| **Cost Format** | INR (₹) and USD ($) |
| **Customization** | Adapts recommendations to soil type, weather, and risk severity |

### 5. RAG Chatbot (`rag_chatbot.py`)

| Attribute | Value |
|-----------|-------|
| **LLM** | Ollama phi (phi2 family, 3B parameters, Q4_0 quantization) |
| **Retrieval** | FAISS vector search + keyword fallback |
| **Embeddings** | `all-MiniLM-L6-v2` (sentence-transformers) |
| **Knowledge Base** | 8 agricultural topics (expandable) |
| **Context** | Diagnosis-aware — chatbot knows current crop, disease, and recommendations |
| **Personality** | Friendly agricultural expert ("Agrovee") with emoji-rich, structured responses |

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12 | Runtime |
| FastAPI | 0.109.2 | Web framework & REST API |
| Uvicorn | 0.27.1 | ASGI server |
| SQLAlchemy | 2.0.25 | ORM & database management |
| SQLite | — | Database (file: `agrovee.db`) |
| PyTorch | 2.1.2 | Deep learning inference |
| torchvision | 0.16.2 | Image transforms & model architectures |
| Pydantic | 2.6.1 | Request/response validation |
| python-jose | 3.3.0 | JWT token creation & verification |
| passlib + bcrypt | 1.7.4 / 4.1.2 | Password hashing |
| httpx | 0.26.0 | Async HTTP client (weather APIs) |
| sentence-transformers | 2.3.1 | Text embeddings for RAG |
| faiss-cpu | 1.7.4 | Vector similarity search |
| Pillow | 10.0.0 | Image processing |
| OpenCV | 4.8.0.76 | Computer vision utilities |
| pytest | 8.0.0 | Testing framework |

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.1.6 | React framework (App Router) |
| React | 19.2.3 | UI library |
| TypeScript | 5.7.3 | Type safety |
| Tailwind CSS | 3.4.17 | Utility-first styling |
| shadcn/ui | — | Pre-built accessible UI components (49 components) |
| Framer Motion | 11.15.0 | Animations & page transitions |
| Axios | 1.13.5 | HTTP client |
| next-themes | 0.4.6 | Dark/light theme switching |
| Recharts | 2.15.0 | Dashboard charts |
| Sonner | 1.7.1 | Toast notifications |
| Lucide React | 0.544.0 | Icon library |
| React Hook Form + Zod | 7.54.1 / 3.24.1 | Form handling & validation |
| Web Speech API | Native | Voice recognition & text-to-speech |

### Infrastructure & External Services

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime (phi model, localhost:11434) |
| OpenWeatherMap API | Real-time weather data |
| Open-Meteo API | Free weather fallback (no API key) |
| Docker + docker-compose | Containerized deployment |

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| Python | 3.10+ (3.12 recommended) | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| npm | 9+ | Package manager |
| Git | Any | Version control |
| Ollama | Latest | Required for RAG chatbot |

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/agrovee.git
cd agrovee
```

### Step 2 — Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY, WEATHER_API_KEY, etc. (see Environment Variables section)

# Initialize the database with default admin user
python scripts/init_db.py
```

### Step 3 — Start Backend Server

```bash
cd backend
source venv/bin/activate

# Development (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
chmod +x start.sh && ./start.sh
```

Backend is now live:
- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

### Step 4 — Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Default API URL is http://localhost:8000/api/v1

# Start development server (Turbopack)
npm run dev
```

Frontend is now live at **http://localhost:3000**

### Step 5 — Ollama Setup (for RAG Chatbot)

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama server
ollama serve

# Pull the phi model (in another terminal)
ollama pull phi
```

Ollama runs at **http://localhost:11434**. The chatbot works without Ollama but falls back to the knowledge base only.

### Step 6 — Login

```
Email:    admin@agrovee.com
Password: admin123
```

> ⚠️ **Change the admin password in production!**

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_NAME` | No | `Agrovee API` | API name shown in docs |
| `ENVIRONMENT` | No | `development` | `development` / `production` |
| `DEBUG` | No | `True` | Enable debug mode |
| `SECRET_KEY` | **Yes** | — | JWT signing key (min 32 chars, random string) |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` | Access token TTL (7 days) |
| `DATABASE_URL` | No | `sqlite:///./agrovee.db` | Database connection string |
| `WEATHER_API_KEY` | **Yes** | — | OpenWeatherMap API key ([get free key](https://openweathermap.org/api)) |
| `MODEL_PATH` | No | `../best_model.pth` | Path to trained ResNet50 model |
| `DEVICE` | No | `cpu` | Inference device (`cpu`, `cuda`, `mps`) |
| `UPLOAD_DIR` | No | `./uploads` | Image upload directory |
| `MAX_UPLOAD_SIZE` | No | `10485760` | Max upload size in bytes (10 MB) |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000,...` | CORS allowed origins |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000/api/v1` | Backend API base URL |

---

## 📡 API Reference

All endpoints are prefixed with `/api/v1`. Protected endpoints require `Authorization: Bearer <access_token>` header.

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | No | Register a new user account |
| `POST` | `/auth/login` | No | Login and receive JWT access + refresh tokens |
| `GET` | `/auth/me` | Yes | Get current authenticated user details |
| `POST` | `/auth/logout` | Yes | Logout (invalidate session) |
| `POST` | `/auth/refresh` | Yes | Refresh access token using refresh token |

### Diagnosis

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/diagnosis/diagnose` | Yes | Upload crop image for AI diagnosis (multipart form: `image`, `soil_type?`, `location?`, `season?`) |
| `GET` | `/diagnosis/diagnose/{id}` | Yes | Retrieve a specific diagnosis result by ID |
| `GET` | `/diagnosis/history` | Yes | Paginated list of user's diagnosis history |
| `GET` | `/diagnosis/recent` | Yes | Get most recent diagnoses |
| `DELETE` | `/diagnosis/diagnose/{id}` | Yes | Delete a diagnosis record |

### Chat

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/chat/message` | Yes | Send a message to the RAG chatbot (with optional session_id and context) |
| `GET` | `/chat/sessions` | Yes | List all chat sessions for the user |
| `GET` | `/chat/sessions/{id}` | Yes | Get a specific session with all messages |
| `DELETE` | `/chat/sessions/{id}` | Yes | Delete a chat session |
| `PUT` | `/chat/sessions/{id}/title` | Yes | Rename a chat session |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/users/profile` | Yes | Get user profile (name, location, farm size) |
| `PUT` | `/users/profile` | Yes | Update user profile |
| `POST` | `/users/change-password` | Yes | Change password |
| `GET` | `/users/stats` | Yes | Get user statistics (diagnosis count, etc.) |
| `DELETE` | `/users/account` | Yes | Deactivate user account |

### System

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | No | Health check — returns service status, version, environment |
| `GET` | `/` | No | Welcome message |
| `GET` | `/api/docs` | No | Swagger UI interactive documentation |
| `GET` | `/api/redoc` | No | ReDoc API documentation |

### Example: Disease Diagnosis Request

```bash
curl -X POST http://localhost:8000/api/v1/diagnosis/diagnose \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image=@/path/to/leaf_photo.jpg" \
  -F "location=Mumbai" \
  -F "soil_type=loamy" \
  -F "season=monsoon"
```

<details>
<summary><strong>Example Response (click to expand)</strong></summary>

```json
{
  "id": 1,
  "predicted_disease": "Tomato___Early_Blight",
  "confidence_score": 98.5,
  "fusion_confidence": 99.2,
  "crop_type": "Tomato",
  "risk_assessment": "HIGH",
  "all_predictions": [
    {"disease": "Tomato___Early_Blight", "confidence": 98.5},
    {"disease": "Tomato___Late_Blight", "confidence": 0.8},
    {"disease": "Tomato___Leaf_Mold", "confidence": 0.3}
  ],
  "weather_data": {
    "temperature": 28.5,
    "humidity": 78.0,
    "rainfall": 2.1,
    "description": "light rain"
  },
  "recommendations": {
    "immediate_actions": [
      "🚨 Isolate affected plants immediately",
      "Remove and destroy infected leaves"
    ],
    "treatments": [
      {
        "type": "Fungicide",
        "name": "Chlorothalonil",
        "application": "Spray every 7-10 days",
        "dosage": "2-3 ml per liter",
        "organic_alternative": "Neem oil (5ml/liter)"
      }
    ],
    "fertilizer_recommendations": [...],
    "irrigation_guidance": [...],
    "preventive_measures": [...],
    "monitoring_schedule": {...},
    "cost_estimate": {
      "estimated_cost_inr": "₹1000 - ₹1500"
    }
  },
  "status": "COMPLETED"
}
```

</details>

---

## 📁 Project Structure

```
Agrovee/
│
├── backend/                          # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry, CORS, routers, health
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py            # Router aggregator
│   │   │       └── endpoints/
│   │   │           ├── auth.py       # Register, login, refresh, logout
│   │   │           ├── chat.py       # Chat message & session endpoints
│   │   │           ├── diagnosis.py  # Image upload & disease diagnosis
│   │   │           └── users.py      # Profile, stats, password
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic settings (env vars)
│   │   │   └── security.py          # JWT creation, verification, password hash
│   │   ├── db/
│   │   │   └── session.py           # SQLAlchemy engine & session
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── user.py              # User table
│   │   │   ├── diagnosis.py         # Diagnosis table
│   │   │   └── chat.py              # ChatSession & ChatMessage tables
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   │   ├── user.py
│   │   │   ├── diagnosis.py
│   │   │   └── chat.py
│   │   └── services/                 # AI service layer
│   │       ├── vision_model.py       # ResNet50 / MobileNetV2 inference
│   │       ├── weather_service.py    # OpenWeatherMap + Open-Meteo
│   │       ├── multimodal_fusion.py  # Vision + weather + soil fusion
│   │       ├── decision_engine.py    # Treatment recommendation engine
│   │       └── rag_chatbot.py        # Ollama RAG chatbot with FAISS
│   ├── tests/                        # pytest test suite (87 tests)
│   │   ├── conftest.py              # Test fixtures & DB setup
│   │   ├── test_auth.py
│   │   ├── test_chat.py
│   │   ├── test_diagnosis.py
│   │   ├── test_health.py
│   │   ├── test_users.py
│   │   └── services/                # AI service unit tests
│   ├── scripts/
│   │   └── init_db.py               # Database initialization + admin user
│   ├── uploads/                      # Uploaded images directory
│   ├── agrovee.db                    # SQLite database file
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Backend container image
│   ├── docker-compose.yml           # Multi-service orchestration
│   ├── Makefile                     # Build/run shortcuts
│   ├── start.sh                     # Server startup script
│   ├── pytest.ini                   # pytest configuration
│   └── .env.example                 # Environment variable template
│
├── frontend/                         # Next.js TypeScript frontend
│   ├── app/
│   │   ├── layout.tsx               # Root layout (providers, fonts, metadata)
│   │   ├── page.tsx                 # Landing page
│   │   ├── globals.css              # Global styles
│   │   ├── login/                   # Login page
│   │   ├── register/                # Registration page
│   │   ├── forgot-password/         # Password reset page
│   │   └── dashboard/
│   │       ├── layout.tsx           # Dashboard layout (sidebar, navbar)
│   │       ├── page.tsx             # Dashboard home (stats, recent activity)
│   │       ├── diagnose/
│   │       │   └── page.tsx         # Crop diagnosis page (upload + results + chat)
│   │       ├── chat/
│   │       │   └── page.tsx         # Full chat page (sessions + messages)
│   │       └── profile/
│   │           └── page.tsx         # User profile management
│   ├── components/
│   │   ├── voice-chat-overlay.tsx   # Full-screen Google-style voice chat
│   │   ├── theme-provider.tsx       # Dark/light theme context
│   │   ├── landing/                 # Landing page sections
│   │   │   ├── navbar.tsx
│   │   │   ├── hero-section.tsx
│   │   │   ├── features-section.tsx
│   │   │   ├── how-it-works-section.tsx
│   │   │   ├── stats-section.tsx
│   │   │   ├── dashboard-preview.tsx
│   │   │   ├── testimonials-section.tsx
│   │   │   ├── cta-section.tsx
│   │   │   └── footer.tsx
│   │   └── ui/                      # shadcn/ui components (49 components)
│   │       ├── button.tsx, card.tsx, dialog.tsx, ...
│   │       └── (accordion, alert, avatar, badge, etc.)
│   ├── lib/
│   │   ├── api.ts                   # Axios-based API client (auth, diagnosis, chat)
│   │   ├── auth-context.tsx         # React auth context (login, register, tokens)
│   │   └── utils.ts                 # Utility functions (cn, formatDate, etc.)
│   ├── hooks/                       # Custom React hooks
│   ├── styles/                      # Additional stylesheets
│   ├── public/                      # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.mjs
│   └── .env.example
│
├── best_model.pth                    # Trained ResNet50 model (283 MB)
├── images/                           # Landing page / promotional images
├── p1/                               # Original training project / model metadata
└── README.md                         # ← You are here
```

---

## 🧪 Testing

The backend has a comprehensive test suite with **87 tests** covering authentication, diagnosis, chat, user management, health checks, and AI services.

### Running Tests

```bash
cd backend
source venv/bin/activate

# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run a specific test file
pytest tests/test_auth.py -v

# Run a specific test
pytest tests/test_health.py::test_health_check -v
```

### Test Coverage Summary

| Module | Coverage |
|--------|----------|
| `app/api/v1/endpoints/` | ~90% |
| `app/core/` | ~85% |
| `app/services/` | ~75% |
| `app/models/` | ~80% |
| **Overall** | **~81%** |

### Test Categories

| File | Tests | Description |
|------|-------|-------------|
| `test_health.py` | 3 | Health endpoint, root endpoint, CORS headers |
| `test_auth.py` | 20+ | Registration, login, token refresh, validation, edge cases |
| `test_diagnosis.py` | 15+ | Image upload, diagnosis flow, history, deletion |
| `test_chat.py` | 15+ | Chat messaging, sessions, context, deletion |
| `test_users.py` | 15+ | Profile CRUD, password change, stats, deactivation |
| `services/` | 10+ | Vision model, weather, fusion, decision engine, RAG |

---

## 🎙️ Voice Chat

Agrovee includes a **Google Assistant–style full-screen voice overlay** for hands-free interaction with the AI chatbot.

### How It Works

1. Click the **microphone button** on the Diagnose or Chat page
2. A full-screen overlay opens with animated visual feedback
3. **Speak your question** — the Web Speech API transcribes in real-time
4. Your question is sent to the RAG chatbot backend
5. The AI response is displayed and **spoken aloud** via text-to-speech
6. Toggle TTS on/off with the speaker button

### Visual States

| State | Color | Indicator |
|-------|-------|-----------|
| **Idle** | White | Tap to speak |
| **Listening** | Green + pulse rings | Actively transcribing |
| **Processing** | Gray | Waiting for AI response |
| **Speaking** | Blue | TTS reading response |

### Technical Details

- Uses the **Web Speech API** (`SpeechRecognition` + `SpeechSynthesis`) — no external service required
- Rendered via **React Portal** (`createPortal`) to ensure full-screen positioning over all content
- Supports continuous recognition and auto-restart
- Browser compatibility: Chrome (best), Edge, Safari (partial)

---

## 🌿 Supported Crops & Diseases (38 Classes)

The vision model recognizes **14 crop types** across **38 disease/healthy classifications**:

| Crop | Classes |
|------|---------|
| 🍎 **Apple** | Apple Scab, Black Rot, Cedar Apple Rust, Healthy |
| 🫐 **Blueberry** | Healthy |
| 🍒 **Cherry** | Powdery Mildew, Healthy |
| 🌽 **Corn** | Cercospora Leaf Spot, Common Rust, Northern Leaf Blight, Healthy |
| 🍇 **Grape** | Black Rot, Esca (Black Measles), Leaf Blight, Healthy |
| 🍊 **Orange** | Haunglongbing (Citrus Greening) |
| 🍑 **Peach** | Bacterial Spot, Healthy |
| 🌶️ **Pepper** | Bacterial Spot, Healthy |
| 🥔 **Potato** | Early Blight, Late Blight, Healthy |
| 🫐 **Raspberry** | Healthy |
| 🫘 **Soybean** | Healthy |
| 🎃 **Squash** | Powdery Mildew |
| 🍓 **Strawberry** | Leaf Scorch, Healthy |
| 🍅 **Tomato** | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Mosaic Virus, Yellow Leaf Curl Virus, Healthy |

---

## 🖼️ Screenshots

> Add screenshots of your running application here:
>
> - Landing page (hero section)
> - Dashboard with stats
> - Diagnosis page with results
> - Chat page with RAG responses
> - Voice chat overlay
> - Dark mode views

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Write tests for new backend endpoints
- Use conventional commit messages
- Keep PR scope focused and small

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for smart farming**

[Report Bug](https://github.com/your-username/agrovee/issues) · [Request Feature](https://github.com/your-username/agrovee/issues) · [Documentation](https://github.com/your-username/agrovee/wiki)

</div>
