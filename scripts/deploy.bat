@echo off
REM TTS项目部署脚本 - Windows版本
REM 用于快速部署到Windows服务器

echo =========================================
echo   TTS 项目部署脚本 (Windows)
echo =========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

REM 部署后端
echo =========================================
echo   步骤 1/2: 部署后端服务
echo =========================================
cd backend

REM 创建虚拟环境
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装Python依赖...
pip install --upgrade pip
pip install -r requirements.txt

REM 创建必要的目录
if not exist data mkdir data
if not exist output mkdir output
if not exist logs mkdir logs

REM 初始化数据库
echo 初始化数据库...
python -c "from src.core.database import init_database; import asyncio; asyncio.run(init_database())"

REM 部署前端
echo.
echo =========================================
echo   步骤 2/2: 部署前端应用
echo =========================================
cd ..\frontend

REM 安装依赖
echo 安装Node依赖...
call npm install

REM 构建生产版本
echo 构建生产版本...
call npm run build

echo.
echo =========================================
echo   部署完成！
echo =========================================
echo.
echo 启动服务:
echo   1. 后端: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn src.main:app
echo   2. 前端: cd frontend ^&^& npm run preview
echo.
echo 或者运行start_server.bat
echo.
pause
