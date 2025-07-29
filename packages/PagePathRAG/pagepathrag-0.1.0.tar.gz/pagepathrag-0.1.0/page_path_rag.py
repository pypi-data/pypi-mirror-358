"""
PagePathRAG - 页面路径检索增强生成系统
用于将UI交互路径转化为知识图谱并进行智能查询的Python库
"""

import os
from typing import List, Dict, Any, Optional, Union
from dataclasses import asdict, dataclass

from PathRAG.PathRAG import PathRAG as InternalPathRAG
from PathRAG.base import QueryParam
from PathRAG.llm import gpt_complete, openai_embedding
from PathRAG.prompt import PROMPTS
from PathRAG.utils import wrap_embedding_func_with_attrs

@dataclass
class PagePathRAGPrompt:
    entity_extraction: str = PROMPTS["entity_extraction"]
    entity_extraction_examples: str = "\n".join(PROMPTS["entity_extraction_examples"])
    summarize_entity_descriptions: str = PROMPTS["summarize_entity_descriptions"]

class PagePathRAG:
    """
    PagePathRAG对外接口类
    
    用于处理UI交互路径文档，构建知识图谱并提供基于关键词的智能查询功能。
    支持自定义LLM和嵌入模型配置。
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
    
    def insert(self, texts: List[str]) -> None:
        """
        插入文本列表到知识图谱中
        
        Args:
            texts (List[str]): 要插入的文本列表，每个文本通常包含UI交互路径描述
            
        Example:
            >>> rag = PagePathRAG(api_key="your-api-key")
            >>> texts = [
            ...     "点击页面底部频道按钮，进入频道tab页。在频道tab页中找到并点击一个新频道，进入该频道主页。",
            ...     "点击设置页面，进入通知设置tab，激活推送通知按钮。"
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
        self._internal_rag.insert(valid_texts)
        print("文本插入完成！")
    
    def query_with_keywords(
        self, 
        keywords: List[str], 
        top_k: int = 40,
        response_type: str = "Multiple Paragraphs",
        return_context_only: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        基于关键词列表进行查询
        
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
            >>> result = rag.query_with_keywords(keywords, top_k=20)
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
        
        print(f"基于关键词 {valid_keywords} 进行查询...")
        result = self._internal_rag.query_with_keywords(valid_keywords, query_param)
        print("查询完成！")
        
        # 根据参数决定返回类型
        if return_context_only and isinstance(result, dict):
            return result.get("context", "")
        
        return result
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储状态信息
        
        Returns:
            Dict[str, Any]: 包含存储配置和状态的字典
        """
        return {
            "working_dir": self._internal_rag.working_dir,
            "working_name": self._internal_rag.working_name,
            "kv_storage": self._internal_rag.kv_storage,
            "vector_storage": self._internal_rag.vector_storage,
            "graph_storage": self._internal_rag.graph_storage,
            "embedding_model": self.embedding_model_name,
            "llm_model": self.model_name
        }
    
    def batch_insert(
        self, 
        chunk_list: List[str], 
        source_name_prefix: str = "batch"
    ) -> None:
        """
        批量插入预分片的文本块
        
        Args:
            chunk_list (List[str]): 预分片的文本块列表
            source_name_prefix (str): 源文档名称前缀，用于生成doc_id
            
        Example:
            >>> rag = PagePathRAG(api_key="your-api-key")
            >>> chunks = [
            ...     "点击页面底部频道按钮",
            ...     "进入频道tab页",
            ...     "点击新频道进入主页"
            ... ]
            >>> rag.batch_insert(chunks, "ui_flows")
        """
        if not chunk_list:
            raise ValueError("文本块列表不能为空")
        
        if not isinstance(chunk_list, list):
            raise TypeError("chunk_list参数必须是字符串列表")
        
        # 过滤空文本块
        valid_chunks = [chunk.strip() for chunk in chunk_list if chunk and chunk.strip()]
        if not valid_chunks:
            raise ValueError("没有找到有效的文本块")
        
        print(f"开始批量插入 {len(valid_chunks)} 个文本块...")
        self._internal_rag.insert_batch(valid_chunks, source_name_prefix)
        print("批量插入完成！")
    
    def delete_by_entity(self, entity_name: str) -> None:
        """
        根据实体名称删除相关的实体和关系
        
        Args:
            entity_name (str): 要删除的实体名称
            
        Example:
            >>> rag = PagePathRAG(api_key="your-api-key")
            >>> rag.delete_by_entity("频道tab页")
        """
        if not entity_name or not entity_name.strip():
            raise ValueError("实体名称不能为空")
        
        print(f"删除实体 '{entity_name}' 及其相关关系...")
        self._internal_rag.delete_by_entity(entity_name.strip())
        print("删除完成！")
    
    def clear_storage(self) -> None:
        """
        清理所有存储数据
        
        用于解决向量维度不匹配等问题，会删除工作目录下的所有数据文件
        
        Warning:
            这会删除所有已存储的数据，操作不可逆！
        """
        import shutil
        
        if os.path.exists(self._internal_rag.working_dir):
            print(f"正在清理存储目录: {self._internal_rag.working_dir}")
            shutil.rmtree(self._internal_rag.working_dir)
            print("存储已清理完成！请重新插入数据。")
        else:
            print("存储目录不存在，无需清理。")
    
    def get_prompt(self) -> PagePathRAGPrompt:
        """
        获取当前的提示词实例
        
        Returns:
            PagePathRAGPrompt: 当前使用的提示词实例
        """
        return self.prompt
    
    def update_prompt(self, prompt: PagePathRAGPrompt) -> None:
        """
        更新提示词实例
        
        Args:
            prompt: 新的提示词实例
            
        Example:
            >>> rag = PagePathRAG(api_key="your-api-key")
            >>> new_prompt = PagePathRAGPrompt(
            ...     entity_extraction="自定义实体抽取提示词...",
            ...     entity_extraction_examples="自定义示例...",
            ...     summarize_entity_descriptions="自定义总结提示词..."
            ... )
            >>> rag.update_prompt(new_prompt)
        """
        self.prompt = prompt
        # 重新设置prompts
        self._setup_prompts()
        print("已更新提示词实例")


# 提供便捷的工厂函数
def create_page_path_rag(
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
    embedding_model_name: str = "text-embedding-3-small",
    model_name: str = "gpt-4o-mini",
    working_name: str = "default",
    working_dir: str = "data/result",
    embedding_dim: Optional[int] = None,
    prompt: Optional[PagePathRAGPrompt] = None
) -> PagePathRAG:
    """
    创建PagePathRAG实例的便捷函数
    
    Args:
        api_key (str): API密钥
        base_url (str): API基础URL
        embedding_model_name (str): 嵌入模型名称
        model_name (str): 语言模型名称
        working_name (str): 工作空间名称
        working_dir (str): 工作目录路径
        embedding_dim (int, optional): 嵌入向量维度，如果不提供则根据模型名称自动推断
        prompt (PagePathRAGPrompt, optional): 提示词dataclass实例
        
    Returns:
        PagePathRAG: 配置好的PagePathRAG实例
    """
    return PagePathRAG(
        api_key=api_key,
        base_url=base_url,
        embedding_model_name=embedding_model_name,
        model_name=model_name,
        working_name=working_name,
        working_dir=working_dir,
        embedding_dim=embedding_dim if embedding_dim is not None else 1024,
        prompt=prompt
    )


# 导出主要类和函数
__all__ = ["PagePathRAG", "PagePathRAGPrompt", "create_page_path_rag"] 