#!/bin/bash
# 文明纪元 - 启动脚本
# 自动使用 venv 隔离的 Python 环境

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活 (venv)"
else
    echo "⚠️  未找到 venv，使用系统 Python"
fi

# 如果 .env 存在则加载
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✅ 环境变量已加载"
fi

echo "🌍 文明纪元 启动中..."
echo "   ARK key: ${ARK_API_KEY:0:8}..."
echo "   OpenRouter key: ${OPENROUTER_API_KEY:0:10}..."
echo ""

# 启动服务
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
