#!/bin/bash

# TTS项目部署脚本
# 用于快速部署到Linux服务器

set -e  # 遇到错误立即退出

echo "========================================="
echo "  TTS 项目部署脚本"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用sudo运行此脚本${NC}"
    exit 1
fi

# 检查操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VERSION=$VERSION_ID
    echo -e "${GREEN}检测到操作系统: $OS $VERSION${NC}"
else
    echo -e "${RED}无法检测操作系统${NC}"
    exit 1
fi

# 更新系统
echo ""
echo "========================================="
echo "  步骤 1/8: 更新系统"
echo "========================================="
apt update && apt upgrade -y

# 安装依赖
echo ""
echo "========================================="
echo "  步骤 2/8: 安装系统依赖"
echo "========================================="
apt install -y python3.10 python3.10-venv python3-pip nodejs npm nginx git

# 安装Python 3.10（如果默认版本低于3.10）
if ! python3.10 --version &> /dev/null; then
    echo "安装Python 3.10..."
    apt install -y software-properties-common
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update
    apt install -y python3.10 python3.10-venv python3.10-dev
fi

# 创建项目目录
echo ""
echo "========================================="
echo "  步骤 3/8: 创建项目目录"
echo "========================================="
PROJECT_DIR="/opt/tts"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}项目目录已存在，是否继续？(y/n)${NC}"
    read -r response
    if [ "$response" != "y" ]; then
        echo "部署取消"
        exit 0
    fi
else
    mkdir -p $PROJECT_DIR
fi
cd $PROJECT_DIR

# 部署后端
echo ""
echo "========================================="
echo "  步骤 4/8: 部署后端服务"
echo "========================================="
cd $PROJECT_DIR/backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
mkdir -p data output logs

# 初始化数据库
python -c "from src.core.database import init_database; import asyncio; asyncio.run(init_database())"

# 创建环境变量文件
if [ ! -f ".env" ]; then
    cat > .env << EOF
DATABASE_URL=sqlite+aiosqlite:///data/tts_history.db
LOG_LEVEL=INFO
MAX_QUEUE_SIZE=10
MAX_HISTORY_SIZE=20
OUTPUT_DIR=output
LOG_DIR=logs
EOF
fi

# 部署前端
echo ""
echo "========================================="
echo "  步骤 5/8: 部署前端应用"
echo "========================================="
cd $PROJECT_DIR/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 配置Nginx
echo ""
echo "========================================="
echo "  步骤 6/8: 配置Nginx"
echo "========================================="
cat > /etc/nginx/sites-available/tts << 'EOF'
server {
    listen 80;
    server_name _;

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
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/tts /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx

# 配置Systemd服务
echo ""
echo "========================================="
echo "  步骤 7/8: 配置系统服务"
echo "========================================="
cat > /etc/systemd/system/tts-backend.service << 'EOF'
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
EOF

# 重新加载systemd
systemctl daemon-reload

# 启用并启动服务
systemctl enable tts-backend
systemctl start tts-backend

# 设置权限
echo ""
echo "========================================="
echo "  步骤 8/8: 设置文件权限"
echo "========================================="
chown -R www-data:www-data /opt/tts/backend/data
chown -R www-data:www-data /opt/tts/backend/output
chown -R www-data:www-data /opt/tts/backend/logs
chmod 755 /opt/tts/backend/data
chmod 755 /opt/tts/backend/output
chmod 755 /opt/tts/backend/logs

# 配置防火墙
echo ""
echo "========================================="
echo "  配置防火墙"
echo "========================================="
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo -e "${GREEN}UFW防火墙规则已添加${NC}"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
    echo -e "${GREEN}Firewalld防火墙规则已添加${NC}"
else
    echo -e "${YELLOW}未检测到防火墙，请手动配置${NC}"
fi

# 验证部署
echo ""
echo "========================================="
echo "  验证部署"
echo "========================================="
sleep 3

# 检查后端服务
if systemctl is-active --quiet tts-backend; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务启动失败${NC}"
    systemctl status tts-backend
fi

# 检查Nginx服务
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx服务运行正常${NC}"
else
    echo -e "${RED}✗ Nginx服务启动失败${NC}"
    systemctl status nginx
fi

# 检查API健康状态
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ 后端API响应正常${NC}"
else
    echo -e "${RED}✗ 后端API无响应${NC}"
fi

# 完成
echo ""
echo "========================================="
echo -e "${GREEN}  部署完成！${NC}"
echo "========================================="
echo ""
echo "后端服务: http://localhost:8000"
echo "前端应用: http://$(hostname -I | awk '{print $1}')"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "管理命令:"
echo "  查看后端日志: journalctl -u tts-backend -f"
echo "  重启后端服务: systemctl restart tts-backend"
echo "  重启Nginx: systemctl restart nginx"
echo ""
echo -e "${YELLOW}注意事项:${NC}"
echo "1. 首次使用音色需要下载模型文件（需要网络连接）"
echo "2. 建议配置HTTPS（使用Certbot）"
echo "3. 定期备份数据库和音频文件"
echo ""
