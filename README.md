# 离线文字转语音工具 (TTS)

一个离线的文字转语音工具,支持中文和英文文本转换为MP3音频文件。

## 技术栈

### 后端
- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 + SQLite
- edge-tts
- asyncio

### 前端
- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia

## 项目结构

```
tts/
├── backend/                   # 后端服务
│   ├── src/
│   │   ├── api/              # API路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑
│   │   └── core/             # 核心配置
│   ├── tests/                # 测试
│   ├── data/                 # 数据库
│   ├── output/               # 音频文件
│   └── logs/                 # 日志
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/       # Vue组件
│   │   ├── views/            # 页面
│   │   ├── services/         # API服务
│   │   └── stores/           # 状态管理
│   └── tests/                # 测试
└── specs/                     # 规范文档
```

## 快速开始

### 方式1: 使用setup脚本 (推荐)

**Windows**:
```bash
setup.bat
```

**Linux/macOS**:
```bash
chmod +x setup.sh
./setup.sh
```

### 方式2: 手动设置

#### 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建环境变量
cp .env.example .env
```

#### 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 创建环境变量
cp .env.example .env.development
```

## 运行开发服务器

### 启动后端服务

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

后端API将在 `http://localhost:8000` 运行

API文档: `http://localhost:8000/docs`

### 启动前端应用

```bash
cd frontend
npm run dev
```

前端应用将在 `http://localhost:5173` 运行

## 功能特性

- ✅ 文本转语音(MP3格式)
- ✅ 语音参数自定义(语速、音调、音量、音色)
- ✅ 任务队列管理
- ✅ 生成历史记录
- ✅ 完全离线运行

## 开发

### 代码规范

**后端**:
```bash
cd backend
black src/
ruff check src/
mypy src/
```

**前端**:
```bash
cd frontend
npm run lint
npm run format
```

### 测试

**后端**:
```bash
cd backend
pytest
```

**前端**:
```bash
cd frontend
npm run test
```

## 文档

- [功能规范](./specs/001-offline-tts/spec.md)
- [实施计划](./specs/001-offline-tts/plan.md)
- [任务分解](./specs/001-offline-tts/tasks.md)
- [快速开始](./specs/001-offline-tts/quickstart.md)
- [API文档](./specs/001-offline-tts/contracts/openapi.yaml)

## 许可证

MIT License
