"""
知识库问答系统配置文件
"""
import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base")
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_PERSIST_DIR = os.path.join(DATA_DIR, "chroma_db")

# API配置
API_HOST = "0.0.0.0"
API_PORT = 8000

# LLM配置 - 支持OpenAI或其他兼容API
# 可以使用本地模型或其他API服务
LLM_CONFIG = {
    # 使用OpenAI API（需要设置OPENAI_API_KEY环境变量）
    # "provider": "openai",
    # "model": "gpt-3.5-turbo",
    
    # 或者使用其他兼容OpenAI API的服务
    "provider": "openai_compatible",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
}

# Embedding配置
EMBEDDING_CONFIG = {
    # 使用本地sentence-transformers模型（无需API Key）
    "provider": "local",  # 或 "openai"
    "model": "all-MiniLM-L6-v2",  # 本地模型，轻量高效
}

# Chroma向量数据库配置
CHROMA_CONFIG = {
    "persist_directory": CHROMA_PERSIST_DIR,
    "collection_name": "knowledge_base",
}

# 文本分割配置
TEXT_SPLITTER_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
}

# 检索配置
RETRIEVAL_CONFIG = {
    "top_k": 5,  # 返回最相关的K个文档片段
    "score_threshold": 0.5,  # 相似度阈值
}
