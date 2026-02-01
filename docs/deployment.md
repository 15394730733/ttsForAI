# 部署文档

## 目录

- [部署概述](#部署概述)
- [环境要求](#环境要求)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker部署](#docker部署)
- [配置说明](#配置说明)
- [性能优化](#性能优化)
- [监控和日志](#监控和日志)
- [故障排查](#故障排查)
- [备份和恢复](#备份和恢复)

---

## 部署概述

离线文字转语音工具采用前后端分离架构，可以灵活部署到各种环境。

### 架构说明

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│  Frontend   │ (Vue 3 SPA)
│  (Port 5173)│
└──────┬──────┘
       │ API Calls
┌──────▼──────┐
│   Backend   │ (FastAPI)
│  (Port 8000)│
└──────┬──────┘
       │
┌──────▼──────┐
│  SQLite DB  │
│edge-tts Eng │
└─────────────┘
```

### 部署模式

1. **开发模式**: 前后端分离运行，适合开发调试
2. **单机部署**: 前后端部署在同一台服务器
3. **Docker部署**: 使用容器化部署，简化环境配置
4. **云服务部署**: 部署到云平台（如阿里云、腾讯云）

---

## 环境要求

### 系统要求

- **操作系统**: Linux / macOS / Windows
- **CPU**: 2核心或以上
- **内存**: 4GB或以上
- **磁盘**: 10GB可用空间（用于音色模型缓存和音频文件）

### 软件要求

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境 |
| npm | 9+ | 包管理器 |
| SQLite | 3.x | 数据库（Python自带） |

### 网络要求

- **首次使用**: 需要互联网连接下载音色模型（50-100MB/音色）
- **正常运行**: 完全离线，无需网络连接

---

## 开发环境部署

### 快速启动

#### 1. 克隆项目

```bash
git clone <repository-url>
cd tts
```

#### 2. 后端设置

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

# 初始化数据库
python -c "from src.core.database import init_database; import asyncio; asyncio.run(init_database())"
```

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.development
```

#### 4. 启动服务

**终端1 - 启动后端**:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**终端2 - 启动前端**:
```bash
cd frontend
npm run dev
```

#### 5. 访问应用

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 生产环境部署

### 方案1: 手动部署

#### 步骤1: 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# 或
sudo yum update -y  # CentOS/RHEL

# 安装Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# 安装Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装Nginx（可选，用于反向代理）
sudo apt install nginx -y
```

#### 步骤2: 部署后端

```bash
# 创建项目目录
sudo mkdir -p /opt/tts
sudo chown $USER:$USER /opt/tts
cd /opt/tts

# 复制后端代码
cp -r /path/to/backend/* .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from src.core.database import init_database; import asyncio; asyncio.run(init_database())"

# 创建必要的目录
mkdir -p data output logs

# 配置环境变量
cat > .env << EOF
DATABASE_URL=sqlite+aiosqlite:///data/tts_history.db
LOG_LEVEL=INFO
MAX_QUEUE_SIZE=10
MAX_HISTORY_SIZE=20
OUTPUT_DIR=output
LOG_DIR=logs
EOF
```

#### 步骤3: 部署前端

```bash
# 复制前端代码
cd /opt/tts
cp -r /path/to/frontend/* .

# 安装依赖
npm install

# 构建生产版本
npm run build

# 构建结果在 dist/ 目录
```

#### 步骤4: 配置Nginx

```bash
# 创建Nginx配置
sudo nano /etc/nginx/sites-available/tts
```

Nginx配置文件内容:

```nginx
# 前端静态文件
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /opt/tts/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000;
    }

    # 后端API文档（可选，生产环境建议关闭）
    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

启用配置:

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/tts /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

#### 步骤5: 配置Systemd服务

创建后端服务文件:

```bash
sudo nano /etc/systemd/system/tts-backend.service
```

服务文件内容:

```ini
[Unit]
Description=TTS Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tts/backend
Environment="PATH=/opt/tts/backend/venv/bin"
ExecStart=/opt/tts/backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动服务:

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable tts-backend

# 启动服务
sudo systemctl start tts-backend

# 检查状态
sudo systemctl status tts-backend
```

#### 步骤6: 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

#### 步骤7: 配置HTTPS（可选）

使用Let's Encrypt免费证书:

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## Docker部署

### 创建Dockerfile

#### 后端Dockerfile

创建 `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY . .

# 创建必要的目录
RUN mkdir -p data output logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端Dockerfile

创建 `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建结果
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 创建docker-compose.yml

在项目根目录创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: tts-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
      - ./backend/output:/app/output
      - ./backend/logs:/app/logs
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///data/tts_history.db
      - LOG_LEVEL=INFO
      - MAX_QUEUE_SIZE=10
      - MAX_HISTORY_SIZE=20
      - OUTPUT_DIR=output
      - LOG_DIR=logs
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: tts-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 构建和启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

---

## 配置说明

### 后端配置

#### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DATABASE_URL | sqlite+aiosqlite:///data/tts_history.db | 数据库连接URL |
| LOG_LEVEL | INFO | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| MAX_QUEUE_SIZE | 10 | 任务队列最大容量 |
| MAX_HISTORY_SIZE | 20 | 历史记录最大保存数量 |
| OUTPUT_DIR | output | 音频文件输出目录 |
| LOG_DIR | logs | 日志文件目录 |

#### 配置文件

创建 `backend/.env`:

```bash
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///data/tts_history.db

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs

# 队列配置
MAX_QUEUE_SIZE=10

# 历史记录配置
MAX_HISTORY_SIZE=20

# 文件存储配置
OUTPUT_DIR=output
```

### 前端配置

#### 环境变量

| 变量名 | 默认值 | 说明 |
|------|--------|------|
| VITE_API_BASE_URL | http://localhost:8000/api/v1 | 后端API地址 |

创建 `frontend/.env.production`:

```bash
# 生产环境API地址
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

---

## 性能优化

### 后端优化

#### 1. 使用生产级ASGI服务器

安装 Gunicorn:

```bash
pip install gunicorn uvicorn[standard]
```

启动命令:

```bash
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### 2. 数据库优化

```python
# 在 backend/src/core/database.py 中配置
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,          # 连接池大小
    max_overflow=40,       # 最大溢出连接数
    connect_args={"check_same_thread": False}
)
```

#### 3. 日志优化

```python
# 在 backend/src/core/logger.py 中配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'logs/tts_app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
    ]
)
```

### 前端优化

#### 1. 构建优化

在 `frontend/vite.config.ts` 中配置:

```typescript
export default defineConfig({
  build: {
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'element-plus': ['element-plus']
        }
      }
    },
    // 压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    // chunk大小警告阈值
    chunkSizeWarningLimit: 1000
  }
})
```

#### 2. CDN加速

生产环境可以将Element Plus等库改为CDN引入:

```html
<head>
  <link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css" />
</head>
<body>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <script src="https://unpkg.com/element-plus"></script>
</body>
```

---

## 监控和日志

### 日志管理

#### 后端日志

日志文件位置: `backend/logs/tts_app.log`

查看日志:

```bash
# 实时查看
tail -f backend/logs/tts_app.log

# 查看最后100行
tail -n 100 backend/logs/tts_app.log

# 搜索错误
grep ERROR backend/logs/tts_app.log
```

#### 前端日志

浏览器开发者工具控制台:

```
F12 -> Console
```

### 系统监控

#### 使用htop监控资源

```bash
# 安装
sudo apt install htop -y

# 运行
htop
```

#### 监控磁盘空间

```bash
# 检查磁盘使用
df -h

# 查看目录大小
du -sh backend/output/*
```

---

## 故障排查

### 常见问题

#### 1. 端口被占用

**症状**: 启动失败，提示端口已被使用

**解决**:
```bash
# 查找占用端口的进程
sudo lsof -i :8000
# 或
sudo netstat -tulpn | grep :8000

# 杀死进程
sudo kill -9 <PID>

# 或修改端口
uvicorn src.main:app --port 8001
```

#### 2. 权限问题

**症状**: 无法写入文件或创建目录

**解决**:
```bash
# 修改目录权限
sudo chown -R $USER:$USER /opt/tts
chmod -R 755 /opt/tts/backend/output
chmod -R 755 /opt/tts/backend/logs
```

#### 3. 依赖缺失

**症状**: ImportError或ModuleNotFoundError

**解决**:
```bash
# 重新安装依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

#### 4. 数据库锁定

**症状**: sqlite3.OperationalError: database is locked

**解决**:
```bash
# 检查是否有其他进程在使用
lsof backend/data/tts_history.db

# 重启后端服务
sudo systemctl restart tts-backend
```

#### 5. 内存不足

**症状**: OOM (Out of Memory) 错误

**解决**:
```bash
# 检查内存使用
free -h

# 减少worker数量
gunicorn src.main:app --workers 2

# 或增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 备份和恢复

### 数据备份

#### 1. 数据库备份

```bash
# 备份SQLite数据库
cp backend/data/tts_history.db backup/tts_history_$(date +%Y%m%d_%H%M%S).db

# 或使用SQLite命令
sqlite3 backend/data/tts_history.db ".backup backup/tts_history_$(date +%Y%m%d_%H%M%S).db"
```

#### 2. 音频文件备份

```bash
# 备份音频文件
tar -czf backup/audio_$(date +%Y%m%d_%H%M%S).tar.gz backend/output/
```

#### 3. 自动备份脚本

创建 `scripts/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/tts"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/tts/backend/data/tts_history.db $BACKUP_DIR/tts_history_$DATE.db

# 备份音频文件（可选）
tar -czf $BACKUP_DIR/audio_$DATE.tar.gz /opt/tts/backend/output/

# 保留最近7天的备份
find $BACKUP_DIR -mtime +7 -delete

echo "Backup completed: $DATE"
```

设置定时任务:

```bash
# 添加到crontab（每天凌晨2点备份）
crontab -e

# 添加以下行
0 2 * * * /opt/tts/scripts/backup.sh
```

### 数据恢复

```bash
# 停止服务
sudo systemctl stop tts-backend

# 恢复数据库
cp backup/tts_history_20260129_020000.db backend/data/tts_history.db

# 恢复音频文件
tar -xzf backup/audio_20260129_020000.tar.gz -C /

# 重启服务
sudo systemctl start tts-backend
```

---

## 安全建议

### 1. 生产环境检查清单

- [ ] 关闭DEBUG模式
- [ ] 使用HTTPS
- [ ] 配置防火墙
- [ ] 限制API访问频率
- [ ] 定期更新依赖
- [ ] 配置日志轮转
- [ ] 设置定期备份
- [ ] 监控系统资源

### 2. API安全

- [ ] 关闭生产环境的API文档（/docs）
- [ ] 实施API访问频率限制
- [ ] 验证所有输入
- [ ] 使用环境变量管理敏感配置

### 3. 文件系统安全

```bash
# 设置适当的文件权限
chmod 600 backend/.env
chmod 700 backend/data
chmod 755 backend/output
chmod 755 backend/logs
```

---

## 更新和升级

### 滚动更新

```bash
# 1. 备份当前版本
./scripts/backup.sh

# 2. 拉取最新代码
git pull origin main

# 3. 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. 更新前端依赖
cd ../frontend
npm install

# 5. 重新构建前端
npm run build

# 6. 重启服务
sudo systemctl restart tts-backend
sudo systemctl reload nginx
```

---

## 性能测试

### 压力测试

使用Apache Bench进行压力测试:

```bash
# 安装
sudo apt install apache2-utils -y

# 测试API端点
ab -n 1000 -c 10 http://localhost:8000/health

# 测试TTS生成
ab -n 100 -c 5 -p test_request.json -T application/json http://localhost:8000/api/v1/tts/generate
```

---

## 联系支持

如遇到部署问题，请：

1. 查看日志文件: `backend/logs/tts_app.log`
2. 查看[常见问题](./user-guide.md#常见问题)
3. 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)

---

**部署愉快！** 🚀
