#!/bin/bash
# Setup script for SEO Analyzer development environment

echo "🚀 Setting up SEO Analyzer..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy models
echo "🔤 Downloading spaCy language models..."
python -m spacy download uk_core_news_sm
python -m spacy download en_core_web_sm

# Initialize database
echo "💾 Initializing database..."
python -c "from database import init_db; init_db()"

echo "✨ Setup complete!"
echo ""
echo "To start the backend server:"
echo "  cd backend"
echo "  ENV=development uvicorn main:app --reload --port 8000"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  python -m http.server 8080"
