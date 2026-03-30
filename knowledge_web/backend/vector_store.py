"""
向量存储模块 - 使用Chroma和LangChain
"""
import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import (
    KNOWLEDGE_BASE_DIR,
    CHROMA_PERSIST_DIR,
    EMBEDDING_CONFIG,
    CHROMA_CONFIG,
    TEXT_SPLITTER_CONFIG,
    RETRIEVAL_CONFIG
)


class VectorStore:
    """向量存储管理类"""
    
    def __init__(self):
        self.embeddings = self._init_embeddings()
        self.vectorstore: Optional[Chroma] = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=TEXT_SPLITTER_CONFIG["chunk_size"],
            chunk_overlap=TEXT_SPLITTER_CONFIG["chunk_overlap"],
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
        
    def _init_embeddings(self):
        """初始化Embedding模型"""
        if EMBEDDING_CONFIG["provider"] == "openai":
            return OpenAIEmbeddings()
        else:
            # 使用本地HuggingFace模型
            return HuggingFaceEmbeddings(
                model_name=EMBEDDING_CONFIG["model"],
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
    
    def load_documents_from_dir(self, directory: str = None) -> List[Document]:
        """从目录加载文档"""
        documents = []
        directory = directory or KNOWLEDGE_BASE_DIR
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建知识库目录: {directory}")
            return documents
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 根据文件类型处理
                    if filename.endswith('.md'):
                        doc = Document(
                            page_content=content,
                            metadata={"source": filename, "type": "markdown"}
                        )
                    elif filename.endswith('.txt'):
                        doc = Document(
                            page_content=content,
                            metadata={"source": filename, "type": "text"}
                        )
                    else:
                        continue
                    
                    documents.append(doc)
                    print(f"加载文档: {filename}")
                except Exception as e:
                    print(f"加载文档失败 {filename}: {e}")
        
        return documents
    
    def build_vectorstore(self, documents: List[Document] = None):
        """构建向量存储"""
        if documents is None:
            documents = self.load_documents_from_dir()
        
        if not documents:
            print("没有文档可处理")
            return None
        
        # 分割文档
        split_docs = []
        for doc in documents:
            chunks = self.text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                split_docs.append(Document(
                    page_content=chunk,
                    metadata={**doc.metadata, "chunk_id": i}
                ))
        
        print(f"文档分割完成: {len(documents)} 个文档 -> {len(split_docs)} 个片段")
        
        # 创建向量存储
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=CHROMA_CONFIG["collection_name"]
        )
        
        print(f"向量存储构建完成，保存到: {CHROMA_PERSIST_DIR}")
        return self.vectorstore
    
    def load_vectorstore(self):
        """加载已有的向量存储"""
        if os.path.exists(CHROMA_PERSIST_DIR):
            self.vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings,
                collection_name=CHROMA_CONFIG["collection_name"]
            )
            return self.vectorstore
        return None
    
    def similarity_search(self, query: str, top_k: int = None) -> List[Document]:
        """相似度搜索"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            return []
        
        top_k = top_k or RETRIEVAL_CONFIG["top_k"]
        results = self.vectorstore.similarity_search(query, k=top_k)
        return results
    
    def similarity_search_with_score(self, query: str, top_k: int = None):
        """带分数的相似度搜索"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            return []
        
        top_k = top_k or RETRIEVAL_CONFIG["top_k"]
        results = self.vectorstore.similarity_search_with_score(query, k=top_k)
        return results


# 全局向量存储实例
_vector_store = None

def get_vector_store() -> VectorStore:
    """获取向量存储实例"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        _vector_store.load_vectorstore() or _vector_store.build_vectorstore()
    return _vector_store


if __name__ == "__main__":
    # 测试
    vs = VectorStore()
    vs.build_vectorstore()
