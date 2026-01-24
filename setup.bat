@echo off
REM Setup script for TTS project (Windows)

echo 🚀 Setting up TTS project...

REM Backend setup
echo 📦 Setting up backend...
cd backend

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env from example if not exists
if not exist ".env" (
    copy .env.example .env
    echo Created .env file from .env.example
)

cd ..

REM Frontend setup
echo 📦 Setting up frontend...
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

REM Create .env from example if not exists
if not exist ".env.development" (
    copy .env.example .env.development
    echo Created .env.development file from .env.example
)

cd ..

echo ✅ Setup complete!
echo.
echo To start the development servers:
echo   Backend:  cd backend ^&^& venv\Scripts\activate ^&^& uvicorn src.main:app --reload
echo   Frontend: cd frontend ^&^& npm run dev
