"""
PagePathRAG - 页面路径检索增强生成系统
用于将UI交互路径转化为知识图谱并进行智能查询的Python库
"""

import os
from typing import List, Dict, Any, Optional, Union
from dataclasses import asdict, dataclass

from .PathRAG.PathRAG import PathRAG as InternalPathRAG
from .PathRAG.base import QueryParam
from .PathRAG.llm import gpt_complete, openai_embedding
from .PathRAG.prompt import PROMPTS
from .PathRAG.utils import wrap_embedding_func_with_attrs

@dataclass
class PagePathRAGPrompt:
    entity_extraction: str = PROMPTS["entity_extraction"]
    entity_extraction_examples: str = "\n".join(PROMPTS["entity_extraction_examples"])
    summarize_entity_descriptions: str = PROMPTS["summarize_entity_descriptions"]

class PagePathRAG:
    """
    PagePathRAG - 页面路径检索增强生成系统
    
    用于处理UI交互路径文档，构建知识图谱并提供基于关键词的智能查询功能。
    支持自定义LLM和嵌入模型配置。
    
    对外提供两个核心接口：
    - insert(texts): 插入文本到知识图谱中
    - query_with_paths(keywords): 基于关键词查询相关的UI路径
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        embedding_model_name: str = "bge-large-zh",
        model_name: str = "gpt-4.1",
        working_name: str = "default",
        working_dir: str = "data/result",
        embedding_dim: int = 1024,
        prompt: Optional[PagePathRAGPrompt] = None
    ):
        """
        初始化PagePathRAG实例
        
        Args:
            api_key (str): API密钥
            base_url (str): API基础URL，默认为OpenAI API
            embedding_model_name (str): 嵌入模型名称
            model_name (str): 语言模型名称
            working_name (str): 工作空间名称，用于区分不同项目
            working_dir (str): 工作目录路径
            embedding_dim (int, optional): 嵌入向量维度
            prompt (PagePathRAGPrompt, optional): 提示词dataclass实例，默认使用prompt文件中的内容
        """
        self.api_key = api_key
        self.base_url = base_url
        self.embedding_model_name = embedding_model_name
        self.model_name = model_name
        self.working_name = working_name
        self.working_dir = working_dir
        self.embedding_dim = embedding_dim
        
        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url
        
        # 初始化prompt实例
        self.prompt = prompt if prompt is not None else PagePathRAGPrompt()
        
        # 设置prompts
        self._setup_prompts()
        
        # 配置LLM函数
        def custom_llm_complete(*args, **kwargs):
            # 移除可能重复的参数，优先使用实例配置
            kwargs.pop("model", None)  # 移除可能存在的model参数
            kwargs["base_url"] = self.base_url
            kwargs["api_key"] = self.api_key
            kwargs["model_name"] = self.model_name  # 使用model_name参数
            return gpt_complete(*args, **kwargs)
        
        # 确定向量维度：优先使用用户设置，否则根据模型名称自动推断
        if self.embedding_dim is not None:
            embedding_dim = self.embedding_dim
        
        # 配置嵌入函数
        @wrap_embedding_func_with_attrs(embedding_dim=embedding_dim, max_token_size=8192)
        async def custom_embedding(*args, **kwargs):
            kwargs.setdefault("model", self.embedding_model_name)
            kwargs.setdefault("base_url", self.base_url)
            kwargs.setdefault("api_key", self.api_key)
            return await openai_embedding(*args, **kwargs)
        
        # 初始化内部PathRAG实例
        self._internal_rag = InternalPathRAG(
            working_dir=working_dir,
            working_name=working_name,
            embedding_func=custom_embedding,
            llm_model_func=custom_llm_complete,
            llm_model_name=model_name,
            llm_model_kwargs={}  # 清空kwargs，避免参数重复
        )
    
    def _setup_prompts(self):
        """
        设置提示词配置
        """
        # 将prompt实例的内容设置到PROMPTS中
        PROMPTS["entity_extraction"] = self.prompt.entity_extraction
        PROMPTS["entity_extraction_examples"] = self.prompt.entity_extraction_examples.split("\n") if isinstance(self.prompt.entity_extraction_examples, str) else self.prompt.entity_extraction_examples
        PROMPTS["summarize_entity_descriptions"] = self.prompt.summarize_entity_descriptions
    

    
    def query_with_paths(
        self, 
        keywords: List[str], 
        top_k: int = 40,
        response_type: str = "Multiple Paragraphs",
        return_context_only: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        基于关键词列表查询相关的UI路径
        
        Args:
            keywords (List[str]): 关键词列表，用于检索相关的UI交互路径
            top_k (int): 返回top-k个最相关的结果，默认40
            response_type (str): 响应类型，默认"Multiple Paragraphs"
            return_context_only (bool): 是否只返回上下文，不生成回答，默认False
            
        Returns:
            Union[str, Dict[str, Any]]: 
                - 如果return_context_only=True，返回上下文字符串
                - 否则返回包含完整查询结果的字典，包含context、documents、path_entities等字段
            
        Example:
            >>> rag = PagePathRAG(api_key="your-api-key")
            >>> keywords = ["频道", "设置", "通知"]
            >>> result = rag.query_with_paths(keywords, top_k=20)
            >>> print(result)
        """
        if not keywords:
            raise ValueError("关键词列表不能为空")
        
        if not isinstance(keywords, list):
            raise TypeError("keywords参数必须是字符串列表")
        
        # 过滤空关键词
        valid_keywords = [kw.strip() for kw in keywords if kw and kw.strip()]
        if not valid_keywords:
            raise ValueError("没有找到有效的关键词")
        
        # 配置查询参数
        query_param = QueryParam(
            mode="hybrid",
            top_k=top_k,
            response_type=response_type,
            only_need_context=return_context_only
        )
        
        print(f"基于关键词 {valid_keywords} 查询相关UI路径...")
        result = self._internal_rag.query_with_keywords(valid_keywords, query_param)
        print("查询完成！")
        
        # 根据参数决定返回类型
        if return_context_only and isinstance(result, dict):
            return result.get("context", "")
        
        return result
    

    
    def insert(self, texts: List[str]) -> None:
        """
        插入文本到知识图谱中
        
        Args:
            texts (List[str]): 文本列表，每个文本通常包含UI交互路径描述
            
        Example:
            >>> rag = PagePathRAG(api_key="your-api-key")
            >>> texts = [
            ...     "从A页面点击B按钮进入B页面",
            ...     "在B页面选择C选项后跳转到C页面",
            ...     "从C页面点击返回按钮回到B页面"
            ... ]
            >>> rag.insert(texts)
        """
        if not texts:
            raise ValueError("文本列表不能为空")
        
        if not isinstance(texts, list):
            raise TypeError("texts参数必须是字符串列表")
        
        # 过滤空文本
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        if not valid_texts:
            raise ValueError("没有找到有效的文本内容")
        
        print(f"开始插入 {len(valid_texts)} 个文本到知识图谱中...")
        self._internal_rag.insert_batch(valid_texts, "batch")
        print("文本插入完成！")





# 导出主要类和函数
__all__ = ["PagePathRAG", "PagePathRAGPrompt"] 