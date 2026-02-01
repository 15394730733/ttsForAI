#!/bin/bash

# TTS项目完整测试脚本

echo "========================================="
echo "  TTS 项目测试套件"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local name=$1
    local command=$2

    echo "----------------------------------------"
    echo "测试: $name"
    echo "----------------------------------------"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if eval "$command"; then
        echo -e "${GREEN}✓ $name 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ $name 失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 1. 后端单元测试
echo "========================================="
echo "  后端单元测试"
echo "========================================="
cd backend

run_test "后端单元测试" "pytest tests/unit/ -v --tb=short"

# 2. 后端集成测试
echo ""
echo "========================================="
echo "  后端集成测试"
echo "========================================="

run_test "后端集成测试" "pytest tests/integration/ -v --tb=short"

# 3. 后端契约测试
echo ""
echo "========================================="
echo "  后端契约测试"
echo "========================================="

run_test "后端契约测试" "pytest tests/contract/ -v --tb=short"

# 4. 前端单元测试
echo ""
echo "========================================="
echo "  前端单元测试"
echo "========================================="
cd ../frontend

run_test "前端单元测试" "npm run test -- --run"

# 5. 前端集成测试
echo ""
echo "========================================="
echo "  前端集成测试"
echo "========================================="

run_test "前端集成测试" "npm run test:integration -- --run"

# 6. 代码规范检查
echo ""
echo "========================================="
echo "  代码规范检查"
echo "========================================="
cd ../backend

run_test "后端代码格式检查" "black --check src/"
run_test "后端Linter检查" "ruff check src/"
run_test "后端类型检查" "mypy src/"

cd ../frontend

run_test "前端Linter检查" "npm run lint"

# 7. 安全检查
echo ""
echo "========================================="
echo "  安全检查"
echo "========================================="
cd ../backend

run_test "依赖安全检查" "pip-audit || true"

# 8. 构建测试
echo ""
echo "========================================="
echo "  构建测试"
echo "========================================="
cd ../frontend

run_test "前端构建测试" "npm run build"

# 测试结果汇总
echo ""
echo "========================================="
echo "  测试结果汇总"
echo "========================================="
echo ""
echo -e "总测试数: ${TOTAL_TESTS}"
echo -e "${GREEN}通过: ${PASSED_TESTS}${NC}"
echo -e "${RED}失败: ${FAILED_TESTS}${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}========================================="
    echo "  所有测试通过！"
    echo "=========================================${NC}"
    exit 0
else
    echo -e "${RED}========================================="
    echo "  部分测试失败，请检查日志"
    echo "=========================================${NC}"
    exit 1
fi
