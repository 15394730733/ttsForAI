#!/bin/bash

# TTS项目代码覆盖率检查脚本

echo "========================================="
echo "  代码覆盖率检查"
echo "========================================="
echo ""

# 后端覆盖率检查
echo "========================================="
echo "  后端代码覆盖率"
echo "========================================="
cd backend

# 运行pytest并生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term --cov-report=json tests/

# 显示覆盖率摘要
echo ""
echo "覆盖率报告已生成:"
echo "  - HTML报告: backend/htmlcov/index.html"
echo "  - JSON报告: backend/coverage.json"
echo ""

# 检查覆盖率是否达标
COVERAGE=$(python -c "import json; f=open('coverage.json'); data=json.load(f); f.close(); print(data['totals']['percent_covered'])")
echo "总覆盖率: ${COVERAGE}%"

if (( $(echo "$COVERAGE >= 70" | bc -l) )); then
    echo -e "\033[0;32m✓ 后端覆盖率达标 (>=70%)${NC}"
else
    echo -e "\033[0;31m✗ 后端覆盖率未达标 (<70%)${NC}"
fi

# 前端覆盖率检查
echo ""
echo "========================================="
echo "  前端代码覆盖率"
echo "========================================="
cd ../frontend

# 运行Vitest并生成覆盖率报告
npm run test:coverage

# 显示覆盖率摘要
echo ""
echo "覆盖率报告已生成:"
echo "  - HTML报告: frontend/coverage/index.html"
echo ""

echo "========================================="
echo "  检查完成"
echo "========================================="
