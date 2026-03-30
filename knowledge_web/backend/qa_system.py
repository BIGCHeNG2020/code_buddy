"""
LLM问答模块 - 使用LangChain
"""
import os
from typing import List, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import LLM_CONFIG
from vector_store import get_vector_store


# 系统提示词
SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请根据提供的知识库内容回答用户问题。

要求：
1. 只使用知识库中的信息回答问题
2. 如果知识库中没有相关信息，请明确告知用户"知识库中未找到相关信息"
3. 回答要准确、简洁、有条理
4. 如果有多个相关信息，请综合整理后回答
5. 在回答末尾标注信息来源

知识库内容：
{context}

用户问题：{input}

请基于以上知识库内容回答："""


class QASystem:
    """问答系统类"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm = self._init_llm()
        self.chain = None
        
    def _init_llm(self):
        """初始化LLM"""
        # 检查是否有API Key
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", None)
        
        if not api_key:
            print("警告: 未设置OPENAI_API_KEY，将使用模拟模式")
            return None
        
        return ChatOpenAI(
            model=LLM_CONFIG["model"],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=LLM_CONFIG["max_tokens"],
            api_key=api_key,
            base_url=base_url
        )
    
    def build_chain(self):
        """构建问答链"""
        if self.llm is None:
            return None
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        
        # 创建文档处理链
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        
        # 创建检索器
        retriever = self.vector_store.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        
        # 创建检索链
        self.chain = create_retrieval_chain(retriever, document_chain)
        return self.chain
    
    def ask(self, question: str) -> dict:
        """提问"""
        # 先检索相关文档
        docs = self.vector_store.similarity_search_with_score(question, top_k=5)
        
        if not docs:
            return {
                "answer": "知识库中未找到相关信息，请先添加文档到知识库。",
                "sources": [],
                "has_answer": False
            }
        
        # 如果没有LLM，使用简单的检索匹配模式
        if self.llm is None:
            return self._simple_answer(question, docs)
        
        # 使用LLM生成答案
        try:
            if self.chain is None:
                self.build_chain()
            
            result = self.chain.invoke({"input": question})
            
            return {
                "answer": result.get("answer", ""),
                "sources": [
                    {"content": doc.page_content[:200], "source": doc.metadata.get("source", "")}
                    for doc, score in docs[:3]
                ],
                "has_answer": True
            }
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return self._simple_answer(question, docs)
    
    def _simple_answer(self, question: str, docs: List) -> dict:
        """简单匹配模式（无需LLM）"""
        # 找最相关的文档
        best_docs = sorted(docs, key=lambda x: x[1])[:3]
        
        context = "\n\n".join([doc.page_content for doc, score in best_docs])
        
        answer = f"根据知识库搜索到以下相关内容：\n\n{context}\n\n"
        answer += "（注：这是基于向量相似度的匹配结果，如需更精准的回答，请配置LLM API）"
        
        return {
            "answer": answer,
            "sources": [
                {
                    "content": doc.page_content[:200],
                    "source": doc.metadata.get("source", ""),
                    "score": float(score)
                }
                for doc, score in best_docs
            ],
            "has_answer": True
        }


# 全局问答系统实例
_qa_system = None

def get_qa_system() -> QASystem:
    """获取问答系统实例"""
    global _qa_system
    if _qa_system is None:
        _qa_system = QASystem()
    return _qa_system


if __name__ == "__main__":
    qa = QASystem()
    result = qa.ask("测试问题")
    print(result)
