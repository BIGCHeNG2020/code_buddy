#!/bin/bash

# 知识库问答系统启动脚本

echo "=========================================="
echo "  知识库问答系统启动脚本"
echo "=========================================="

# 进入项目目录
cd "$(dirname "$0")"

# 检查依赖
echo "[1/3] 检查依赖..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -r requirements.txt --quiet
fi

# 初始化向量存储
echo "[2/3] 初始化向量存储..."
cd backend
python -c "
from vector_store import VectorStore
vs = VectorStore()
vs.load_vectorstore() or vs.build_vectorstore()
print('向量存储就绪')
" 2>/dev/null

# 启动服务
echo "[3/3] 启动后端服务..."
echo ""
echo "=========================================="
echo "  服务地址:"
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 前端页面: 请打开 frontend/index.html"
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python main.py
