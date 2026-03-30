# 知识库问答系统

基于 LangChain + Chroma + FastAPI + React 构建的智能知识库问答系统。

## 功能特点

- 📄 支持上传文档（txt、md格式）
- 🔍 基于向量检索的语义搜索
- 💬 智能问答，准确匹配知识库内容
- 🎯 支持配置LLM实现更智能的回答
- 📊 文档管理和索引重建
- 🌐 现代化Web界面

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + Ant Design 5 (CDN方式) |
| 后端 | FastAPI + Uvicorn |
| AI框架 | LangChain |
| 向量数据库 | Chroma |
| Embedding | sentence-transformers (本地) |

## 快速开始

### 1. 安装依赖

```bash
cd knowledge_web
pip install -r requirements.txt
```

### 2. 启动后端

```bash
cd backend
python main.py
```

后端服务将在 http://localhost:8000 启动

### 3. 打开前端

直接在浏览器中打开 `frontend/index.html` 文件，或者使用任意静态服务器：

```bash
cd frontend
python -m http.server 3000
```

然后访问 http://localhost:3000

### 4. 配置LLM（可选）

设置环境变量以启用LLM智能回答：

```bash
export OPENAI_API_KEY=your-api-key
# 如果使用其他兼容接口
export OPENAI_BASE_URL=https://your-api-endpoint
```

如果不配置LLM，系统将工作在检索模式，直接返回相关文档片段。

## 目录结构

```
knowledge_web/
├── backend/
│   ├── main.py          # FastAPI主应用
│   ├── config.py        # 配置文件
│   ├── vector_store.py  # 向量存储模块
│   └── qa_system.py     # 问答系统模块
├── frontend/
│   └── index.html       # 前端页面（React+AntD CDN）
├── knowledge_base/      # 知识库文档目录
│   ├── 产品介绍.txt
│   └── 技术文档.md
├── data/               # 数据存储目录
│   └── chroma_db/      # Chroma向量数据库
└── requirements.txt    # Python依赖
```

## API文档

启动后端后，访问 http://localhost:8000/docs 查看Swagger API文档。

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/status | 获取系统状态 |
| POST | /api/ask | 提问 |
| GET | /api/documents | 获取文档列表 |
| POST | /api/documents/upload | 上传文档 |
| POST | /api/documents/text | 添加文本文档 |
| DELETE | /api/documents/{filename} | 删除文档 |
| POST | /api/rebuild | 重建索引 |

## 使用说明

1. **添加知识**: 通过界面上传文档或直接添加文本
2. **重建索引**: 添加文档后点击"重建索引"
3. **开始提问**: 在对话框中输入问题，系统会检索知识库并回答

## 配置选项

编辑 `backend/config.py` 可以配置：

```python
# LLM配置
LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
}

# Embedding配置
EMBEDDING_CONFIG = {
    "provider": "local",  # 或 "openai"
    "model": "all-MiniLM-L6-v2",
}

# 检索配置
RETRIEVAL_CONFIG = {
    "top_k": 5,
    "score_threshold": 0.5,
}
```

## 注意事项

1. 首次启动时会下载Embedding模型（约90MB）
2. 建议使用Python 3.9+
3. 生产环境建议配置CORS和认证

## License

MIT
