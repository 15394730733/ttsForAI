#!/bin/bash
# Setup script for TTS project

echo "🚀 Setting up TTS project..."

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env from example if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
fi

cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env from example if not exists
if [ ! -f ".env.development" ]; then
    cp .env.example .env.development
    echo "Created .env.development file from .env.example"
fi

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the development servers:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn src.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
