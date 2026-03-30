"""
FastAPI主应用 - 知识库问答系统API
"""
import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import (
    API_HOST, 
    API_PORT, 
    KNOWLEDGE_BASE_DIR, 
    CHROMA_PERSIST_DIR,
    DATA_DIR
)
from qa_system import get_qa_system
from vector_store import get_vector_store


# 创建FastAPI应用
app = FastAPI(
    title="知识库问答系统",
    description="基于LangChain和Chroma的知识库问答系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求/响应模型
class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: List[dict]
    has_answer: bool


class DocumentInfo(BaseModel):
    filename: str
    type: str
    size: int


class SystemStatus(BaseModel):
    documents_count: int
    is_initialized: bool
    has_llm: bool


# API路由
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "知识库问答系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/status", response_model=SystemStatus)
async def get_status():
    """获取系统状态"""
    try:
        qa = get_qa_system()
        vs = get_vector_store()
        
        # 统计知识库文档数量
        docs_count = 0
        if os.path.exists(KNOWLEDGE_BASE_DIR):
            docs_count = len([f for f in os.listdir(KNOWLEDGE_BASE_DIR) 
                            if os.path.isfile(os.path.join(KNOWLEDGE_BASE_DIR, f))])
        
        return {
            "documents_count": docs_count,
            "is_initialized": vs.vectorstore is not None,
            "has_llm": qa.llm is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """提问接口"""
    try:
        qa = get_qa_system()
        result = qa.ask(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """获取知识库文档列表"""
    try:
        documents = []
        if os.path.exists(KNOWLEDGE_BASE_DIR):
            for filename in os.listdir(KNOWLEDGE_BASE_DIR):
                filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
                if os.path.isfile(filepath):
                    doc_type = "markdown" if filename.endswith('.md') else "text"
                    documents.append({
                        "filename": filename,
                        "type": doc_type,
                        "size": os.path.getsize(filepath)
                    })
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档到知识库"""
    try:
        # 检查文件类型
        if not (file.filename.endswith('.txt') or file.filename.endswith('.md')):
            raise HTTPException(
                status_code=400, 
                detail="只支持 .txt 和 .md 格式的文件"
            )
        
        # 确保目录存在
        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
        
        # 保存文件
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, file.filename)
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {"message": f"文件 {file.filename} 上传成功", "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/text")
async def add_text_document(filename: str = Form(...), content: str = Form(...)):
    """添加文本内容作为知识库文档"""
    try:
        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
        
        # 确保文件名正确
        if not filename.endswith('.txt') and not filename.endswith('.md'):
            filename += '.txt'
        
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"message": f"文档 {filename} 添加成功", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """删除知识库文档"""
    try:
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        os.remove(filepath)
        return {"message": f"文件 {filename} 删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rebuild")
async def rebuild_knowledge_base():
    """重建知识库向量索引"""
    try:
        # 清除旧的向量存储
        if os.path.exists(CHROMA_PERSIST_DIR):
            shutil.rmtree(CHROMA_PERSIST_DIR)
        
        # 重新构建
        vs = get_vector_store()
        vs.vectorstore = None  # 清除缓存
        vs.build_vectorstore()
        
        # 重置问答系统
        qa = get_qa_system()
        qa.chain = None
        
        return {"message": "知识库索引重建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_knowledge(query: str, top_k: int = 5):
    """搜索知识库"""
    try:
        vs = get_vector_store()
        results = vs.similarity_search_with_score(query, top_k=top_k)
        
        return {
            "query": query,
            "results": [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", ""),
                    "score": float(score)
                }
                for doc, score in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
