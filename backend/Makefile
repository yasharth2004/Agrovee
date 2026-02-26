# Makefile for Agrovee Backend
# Convenience commands for development and deployment

.PHONY: help install setup run dev docker-up docker-down docker-logs clean test lint format

help:
	@echo "Agrovee Backend - Available Commands"
	@echo "============================================"
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Complete setup (venv, deps, db)"
	@echo "  make run          - Run production server"
	@echo "  make dev          - Run development server (auto-reload)"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean temporary files"

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

setup:
	@echo "🚀 Running complete setup..."
	@chmod +x start.sh
	@./start.sh

run:
	@echo "🚀 Starting production server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

dev:
	@echo "🔧 Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/api/docs"

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "📋 Docker logs..."
	docker-compose logs -f backend

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

lint:
	@echo "🔍 Running linters..."
	flake8 app/
	mypy app/

format:
	@echo "✨ Formatting code..."
	black app/
	@echo "✅ Code formatted!"

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	@echo "✅ Cleaned!"
