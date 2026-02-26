#!/bin/bash

# Agrovee Backend Quick Start Script
# This script sets up and runs the backend server

set -e  # Exit on error

echo "============================================================"
echo "Agrovee Backend - Quick Start"
echo "============================================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your settings."
fi

# Check PostgreSQL connection
echo "🔍 Checking PostgreSQL connection..."
python3 -c "
import sys
sys.path.insert(0, '.')
from app.core.config import settings
from sqlalchemy import create_engine
try:
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    conn.close()
    print('✅ PostgreSQL connection successful!')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    print('   Please ensure PostgreSQL is running and credentials are correct.')
    sys.exit(1)
"

# Initialize database
echo "🔄 Initializing database..."
python3 scripts/init_db.py

# Create upload directory
echo "📁 Creating upload directory..."
mkdir -p uploads logs data/faiss_index data/knowledge_base

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "To start the server:"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/api/docs"
echo ""
echo "Default Admin Credentials:"
echo "  Email: admin@agrovee.com"
echo "  Password: admin123"
echo "  ⚠️  CHANGE PASSWORD IN PRODUCTION!"
echo ""
echo "============================================================"

# Ask if user wants to start server
read -p "Start the development server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting server..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi
