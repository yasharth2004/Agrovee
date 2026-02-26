# 🌾 Agrovee — AI-Powered Smart Farming Assistant

Agrovee is a full-stack multimodal AI platform for **crop health monitoring and disease detection**. Upload a photo of your crop, and the system identifies the crop type, detects diseases using a trained deep learning model, provides treatment recommendations, and offers an AI chatbot for farming advice.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![PyTorch](https://img.shields.io/badge/PyTorch-2.10-red)
![Tests](https://img.shields.io/badge/Tests-87%20Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-81%25-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🔬 Crop Disease Detection** | Upload a leaf/plant image → ResNet50 model identifies crop type and disease with confidence scores |
| **🌤️ Weather-Aware Fusion** | Combines vision predictions with local weather data for enhanced accuracy |
| **💊 Treatment Recommendations** | AI decision engine generates specific treatments, fertilizer guidance, and preventive measures |
| **💬 AI Chatbot** | RAG-powered chatbot answers farming questions with context-aware responses |
| **🔐 Authentication** | JWT-based auth with registration, login, profile management |
| **📊 Dashboard** | View diagnosis history, stats, and recent activity |
| **🌙 Dark Mode** | Full dark/light theme support |

---

## 🏗️ Architecture

```
┌─────────────────┐     REST API     ┌──────────────────────────┐
│   Next.js 16    │ ◄──────────────► │    FastAPI Backend        │
│   React 19      │                  │                          │
│   Tailwind CSS  │                  │  ┌────────────────────┐  │
│   shadcn/ui     │                  │  │  Vision Model      │  │
└─────────────────┘                  │  │  (ResNet50/38 cls)  │  │
                                     │  ├────────────────────┤  │
                                     │  │  Weather Service    │  │
                                     │  ├────────────────────┤  │
                                     │  │  Multimodal Fusion  │  │
                                     │  ├────────────────────┤  │
                                     │  │  Decision Engine    │  │
                                     │  ├────────────────────┤  │
                                     │  │  RAG Chatbot        │  │
                                     │  └────────────────────┘  │
                                     │         SQLite           │
                                     └──────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **Git**

### 1. Clone & Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
cp .env.example .env            # Edit with your secrets
```

### 2. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at **http://localhost:8000** — API docs at **/docs**

### 3. Setup & Start Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # Edit API URL if needed
npm run dev
```

Frontend runs at **http://localhost:3000**

### 4. Default Admin Login

```
Email:    admin@agrovee.com
Password: admin123
```

---

## 🧪 Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v                  # Run all 87 tests
pytest tests/ --cov=app --cov-report=html  # Coverage report
```

---

## 📁 Project Structure

```
Agrovee/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/ # Auth, Diagnosis, Chat, Users
│   │   ├── core/             # Config, Security, Database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # AI services (5 modules)
│   ├── tests/                # 87 tests, 81% coverage
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Next.js frontend
│   ├── app/                  # Pages (dashboard, chat, diagnose, profile)
│   ├── components/           # UI components (shadcn/ui)
│   ├── lib/                  # API client, auth context, utils
│   └── public/               # Static assets
├── best_model.pth            # Trained ResNet50 model (283MB)
└── README.md
```

---

## 🤖 AI Models & Services

| Service | Technology | Description |
|---------|-----------|-------------|
| **Vision Model** | ResNet50 (PyTorch) | 38-class crop disease classifier trained on PlantVillage dataset |
| **Weather Service** | OpenWeatherMap API | Fetches local weather for environmental context |
| **Multimodal Fusion** | Custom algorithm | Combines vision + weather + soil data for enhanced predictions |
| **Decision Engine** | Rule-based AI | Generates treatment plans, fertilizer/irrigation guidance |
| **RAG Chatbot** | Sentence Transformers | Retrieval-Augmented Generation for farming Q&A |

### Supported Crops & Diseases (38 Classes)

Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato

---

## 🔒 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login → JWT tokens |
| GET | `/api/v1/auth/me` | Current user profile |
| POST | `/api/v1/diagnosis/diagnose` | Upload image → disease prediction |
| GET | `/api/v1/diagnosis/history` | Diagnosis history (paginated) |
| POST | `/api/v1/chat/message` | Send chat message |
| GET | `/api/v1/chat/sessions` | List chat sessions |
| GET | `/api/v1/users/profile` | User profile |
| PUT | `/api/v1/users/profile` | Update profile |

Full OpenAPI docs: **http://localhost:8000/docs**

---

## 🛠️ Tech Stack

**Backend:** Python 3.12 · FastAPI · SQLAlchemy · SQLite · PyTorch · JWT  
**Frontend:** Next.js 16 · React 19 · TypeScript · Tailwind CSS · shadcn/ui  
**AI/ML:** ResNet50 · MobileNetV2 (fallback) · Sentence Transformers  
**Testing:** pytest · 87 tests · 81% coverage  

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
