import asyncio
import os
from tqdm.asyncio import tqdm as tqdm_async
from dataclasses import asdict, dataclass, field
from datetime import datetime
from functools import partial
from typing import Type, cast


from .llm import (
    gpt_complete,
    openai_embedding,
)
from .operate import (
    chunking_by_token_size,
    extract_entities,
    kg_query,
)

from .utils import (
    EmbeddingFunc,
    compute_mdhash_id,
    limit_async_func_call,
    convert_response_to_json,
    logger,
    set_logger,
)
from .base import (
    BaseGraphStorage,
    BaseKVStorage,
    BaseVectorStorage,
    StorageNameSpace,
    QueryParam,
)

from .storage import (
    JsonKVStorage,
    NanoVectorDBStorage,
    NetworkXStorage,
)




def lazy_external_import(module_name: str, class_name: str):
    """Lazily import a class from an external module based on the package of the caller."""


    import inspect

    caller_frame = inspect.currentframe().f_back
    module = inspect.getmodule(caller_frame)
    package = module.__package__ if module else None

    def import_class(*args, **kwargs):
        import importlib

  
        module = importlib.import_module(module_name, package=package)


        cls = getattr(module, class_name)
        return cls(*args, **kwargs)

    return import_class


Neo4JStorage = lazy_external_import(".kg.neo4j_impl", "Neo4JStorage")
OracleKVStorage = lazy_external_import(".kg.oracle_impl", "OracleKVStorage")
OracleGraphStorage = lazy_external_import(".kg.oracle_impl", "OracleGraphStorage")
OracleVectorDBStorage = lazy_external_import(".kg.oracle_impl", "OracleVectorDBStorage")
MilvusVectorDBStorge = lazy_external_import(".kg.milvus_impl", "MilvusVectorDBStorge")
MongoKVStorage = lazy_external_import(".kg.mongo_impl", "MongoKVStorage")
ChromaVectorDBStorage = lazy_external_import(".kg.chroma_impl", "ChromaVectorDBStorage")
TiDBKVStorage = lazy_external_import(".kg.tidb_impl", "TiDBKVStorage")
TiDBVectorDBStorage = lazy_external_import(".kg.tidb_impl", "TiDBVectorDBStorage")
AGEStorage = lazy_external_import(".kg.age_impl", "AGEStorage")


def always_get_an_event_loop() -> asyncio.AbstractEventLoop:
    """
    Ensure that there is always an event loop available.

    This function tries to get the current event loop. If the current event loop is closed or does not exist,
    it creates a new event loop and sets it as the current event loop.

    Returns:
        asyncio.AbstractEventLoop: The current or newly created event loop.
    """
    try:

        current_loop = asyncio.get_event_loop()
        if current_loop.is_closed():
            raise RuntimeError("Event loop is closed.")
        return current_loop

    except RuntimeError:

        logger.info("Creating a new event loop in main thread.")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop


@dataclass
class PathRAG:
    working_dir: str = field(default="data/result")
    working_name: str = field(default="")

    embedding_cache_config: dict = field(
        default_factory=lambda: {
            "enabled": False,
            "similarity_threshold": 0.95,
            "use_llm_check": False,
        }
    )
    kv_storage: str = field(default="JsonKVStorage")
    vector_storage: str = field(default="NanoVectorDBStorage")
    graph_storage: str = field(default="NetworkXStorage")

    current_log_level = logger.level
    log_level: str = field(default=current_log_level)


    chunk_token_size: int = 1200
    chunk_overlap_token_size: int = 100
    tiktoken_model_name: str = "gpt-4o-mini"


    entity_extract_max_gleaning: int = 1
    entity_summary_to_max_tokens: int = 500


    node_embedding_algorithm: str = "node2vec"
    node2vec_params: dict = field(
        default_factory=lambda: {
            "dimensions": 1536,
            "num_walks": 10,
            "walk_length": 40,
            "window_size": 2,
            "iterations": 3,
            "random_seed": 3,
        }
    )


    embedding_func: EmbeddingFunc = field(default_factory=lambda: openai_embedding)
    embedding_batch_num: int = 32
    embedding_func_max_async: int = 16
    
    # 批量插入配置
    batch_insert_max_async: int = 8  # 控制批量插入的并发数
    batch_insert_chunk_size: int = 50  # 每个批次处理的chunk数量


    llm_model_func: callable = gpt_complete  
    llm_model_name: str = "meta-llama/Llama-3.2-1B-Instruct"  
    llm_model_max_token_size: int = 32768
    llm_model_max_async: int = 16
    llm_model_kwargs: dict = field(default_factory=dict)


    vector_db_storage_cls_kwargs: dict = field(default_factory=dict)

    enable_llm_cache: bool = True


    addon_params: dict = field(default_factory=dict)
    convert_response_to_json_func: callable = convert_response_to_json

    def __post_init__(self):
        # 处理工作目录路径拼接
        if self.working_name:
            self.working_dir = os.path.join(self.working_dir, self.working_name)
        
        log_file = os.path.join("PathRAG.log")
        set_logger(log_file)
        logger.setLevel(self.log_level)

        logger.info(f"Logger initialized for working directory: {self.working_dir}")


        self.key_string_value_json_storage_cls: Type[BaseKVStorage] = (
            self._get_storage_class()[self.kv_storage]
        )
        self.vector_db_storage_cls: Type[BaseVectorStorage] = self._get_storage_class()[
            self.vector_storage
        ]
        self.graph_storage_cls: Type[BaseGraphStorage] = self._get_storage_class()[
            self.graph_storage
        ]

        if not os.path.exists(self.working_dir):
            logger.info(f"Creating working directory {self.working_dir}")
            os.makedirs(self.working_dir)

        self.llm_response_cache = (
            self.key_string_value_json_storage_cls(
                namespace="llm_response_cache",
                global_config=asdict(self),
                embedding_func=None,
            )
            if self.enable_llm_cache
            else None
        )
        self.embedding_func = limit_async_func_call(self.embedding_func_max_async)(
            self.embedding_func
        )


        self.full_docs = self.key_string_value_json_storage_cls(
            namespace="full_docs",
            global_config=asdict(self),
            embedding_func=self.embedding_func,
        )
        self.text_chunks = self.key_string_value_json_storage_cls(
            namespace="text_chunks",
            global_config=asdict(self),
            embedding_func=self.embedding_func,
        )
        self.chunk_entity_relation_graph = self.graph_storage_cls(
            namespace="chunk_entity_relation",
            global_config=asdict(self),
            embedding_func=self.embedding_func,
        )


        self.entities_vdb = self.vector_db_storage_cls(
            namespace="entities",
            global_config=asdict(self),
            embedding_func=self.embedding_func,
            meta_fields={"entity_name"},
        )
        self.relationships_vdb = self.vector_db_storage_cls(
            namespace="relationships",
            global_config=asdict(self),
            embedding_func=self.embedding_func,
            meta_fields={"src_id", "tgt_id"},
        )
        self.chunks_vdb = self.vector_db_storage_cls(
            namespace="chunks",
            global_config=asdict(self),
            embedding_func=self.embedding_func,
        )

        self.llm_model_func = limit_async_func_call(self.llm_model_max_async)(
            partial(
                self.llm_model_func,
                hashing_kv=self.llm_response_cache
                if self.llm_response_cache
                and hasattr(self.llm_response_cache, "global_config")
                else self.key_string_value_json_storage_cls(
                    global_config=asdict(self),
                ),
                **self.llm_model_kwargs,
            )
        )

    def _get_storage_class(self) -> Type[BaseGraphStorage]:
        return {

            "JsonKVStorage": JsonKVStorage,
            "OracleKVStorage": OracleKVStorage,
            "MongoKVStorage": MongoKVStorage,
            "TiDBKVStorage": TiDBKVStorage,

            "NanoVectorDBStorage": NanoVectorDBStorage,
            "OracleVectorDBStorage": OracleVectorDBStorage,
            "MilvusVectorDBStorge": MilvusVectorDBStorge,
            "ChromaVectorDBStorage": ChromaVectorDBStorage,
            "TiDBVectorDBStorage": TiDBVectorDBStorage,

            "NetworkXStorage": NetworkXStorage,
            "Neo4JStorage": Neo4JStorage,
            "OracleGraphStorage": OracleGraphStorage,
            "AGEStorage": AGEStorage,

        }

    def insert(self, string_or_strings):
        
        loop = always_get_an_event_loop()
        return loop.run_until_complete(self.ainsert(string_or_strings))

    async def ainsert(self, string_or_strings):
        update_storage = False
        try:
            if isinstance(string_or_strings, str):
                string_or_strings = [string_or_strings]

            new_docs = {
                compute_mdhash_id(c.strip(), prefix="doc-"): {"content": c.strip()}
                for c in string_or_strings
            }
            _add_doc_keys = await self.full_docs.filter_keys(list(new_docs.keys()))
            new_docs = {k: v for k, v in new_docs.items() if k in _add_doc_keys}
            if not len(new_docs):
                logger.warning("All docs are already in the storage")
                return
            update_storage = True
            logger.info(f"[New Docs] inserting {len(new_docs)} docs")

            inserting_chunks = {}
            for doc_key, doc in tqdm_async(
                new_docs.items(), desc="Chunking documents", unit="doc"
            ):
                chunks = {
                    compute_mdhash_id(dp["content"], prefix="chunk-"): {
                        **dp,
                        "full_doc_id": doc_key,
                    }
                    for dp in chunking_by_token_size(
                        doc["content"],
                        overlap_token_size=self.chunk_overlap_token_size,
                        max_token_size=self.chunk_token_size,
                        tiktoken_model=self.tiktoken_model_name,
                    )
                }
                inserting_chunks.update(chunks)
            _add_chunk_keys = await self.text_chunks.filter_keys(
                list(inserting_chunks.keys())
            )
            inserting_chunks = {
                k: v for k, v in inserting_chunks.items() if k in _add_chunk_keys
            }
            if not len(inserting_chunks):
                logger.warning("All chunks are already in the storage")
                return
            logger.info(f"[New Chunks] inserting {len(inserting_chunks)} chunks")

            await self.chunks_vdb.upsert(inserting_chunks)

            logger.info("[Entity Extraction]...")
            maybe_new_kg = await extract_entities(
                inserting_chunks,
                knowledge_graph_inst=self.chunk_entity_relation_graph,
                entity_vdb=self.entities_vdb,
                relationships_vdb=self.relationships_vdb,
                global_config=asdict(self),
                show_progress=True,
                use_chinese_progress=False,
            )
            if maybe_new_kg is None:
                logger.warning("No new entities and relationships found")
                return
            self.chunk_entity_relation_graph = maybe_new_kg

            await self.full_docs.upsert(new_docs)
            await self.text_chunks.upsert(inserting_chunks)
        finally:
            if update_storage:
                await self._insert_done()

    def insert_batch(self, chunk_list, source_name_prefix="batch"):
        """
        批量插入预分片的文本块，支持多线程处理
        
        Args:
            chunk_list (List[str]): 预分片的文本块列表，每个str就是一个chunk
            source_name_prefix (str): 源文档名称前缀，用于生成doc_id
        
        Returns:
            None
        """
        loop = always_get_an_event_loop()
        return loop.run_until_complete(self.ainsert_batch(chunk_list, source_name_prefix))

    async def ainsert_batch(self, chunk_list, source_name_prefix="batch"):
        """
        异步批量插入预分片的文本块
        
        Args:
            chunk_list (List[str]): 预分片的文本块列表
            source_name_prefix (str): 源文档名称前缀
        """
        if not chunk_list:
            logger.warning("Empty chunk list provided")
            return
            
        update_storage = False
        try:
            logger.info(f"[Batch Insert] Starting batch insertion of {len(chunk_list)} chunks")
            
            # 创建虚拟文档ID
            doc_id = compute_mdhash_id(f"{source_name_prefix}_{len(chunk_list)}", prefix="doc-")
            new_docs = {doc_id: {"content": f"Batch document with {len(chunk_list)} chunks"}}
            
            # 处理chunks，跳过分词步骤
            inserting_chunks = {}
            logger.info("[Batch Insert] Preparing chunks...")
            
            for i, chunk_content in enumerate(chunk_list):
                if not chunk_content or not chunk_content.strip():
                    logger.warning(f"Skipping empty chunk at index {i}")
                    continue
                    
                chunk_content = chunk_content.strip()
                chunk_id = compute_mdhash_id(chunk_content, prefix="chunk-")
                
                inserting_chunks[chunk_id] = {
                    "content": chunk_content,
                    "full_doc_id": doc_id,
                    "chunk_order_index": i,
                    "tokens": len(chunk_content)  # 简单估算，可以改为更精确的token计算
                }
            
            if not inserting_chunks:
                logger.warning("No valid chunks found after filtering")
                return
                
            # 检查是否有新的chunks需要插入
            _add_chunk_keys = await self.text_chunks.filter_keys(list(inserting_chunks.keys()))
            inserting_chunks = {
                k: v for k, v in inserting_chunks.items() if k in _add_chunk_keys
            }
            
            if not len(inserting_chunks):
                logger.warning("All chunks are already in the storage")
                return
                
            update_storage = True
            logger.info(f"[Batch Insert] Inserting {len(inserting_chunks)} new chunks")
            
            # 分批处理chunks以支持大规模数据
            await self._process_chunks_in_batches(inserting_chunks)
            
            # 批量处理实体抽取
            logger.info("[Batch Insert] Starting entity extraction...")
            maybe_new_kg = await self._extract_entities_in_batches(inserting_chunks)
            
            if maybe_new_kg is not None:
                self.chunk_entity_relation_graph = maybe_new_kg
            else:
                logger.warning("No new entities and relationships found")
            
            # 保存文档和chunks
            await self.full_docs.upsert(new_docs)
            await self.text_chunks.upsert(inserting_chunks)
            
            logger.info(f"[Batch Insert] Successfully completed batch insertion")
            
        except Exception as e:
            logger.error(f"[Batch Insert] Error during batch insertion: {e}")
            raise
        finally:
            if update_storage:
                await self._insert_done()

    async def _process_chunks_in_batches(self, inserting_chunks):
        """分批处理chunks的向量化"""
        chunk_items = list(inserting_chunks.items())
        semaphore = asyncio.Semaphore(self.batch_insert_max_async)
        
        async def process_batch(batch_chunks):
            async with semaphore:
                batch_dict = dict(batch_chunks)
                await self.chunks_vdb.upsert(batch_dict)
                logger.info(f"Processed batch of {len(batch_dict)} chunks")
        
        # 将chunks分成小批次
        tasks = []
        for i in range(0, len(chunk_items), self.batch_insert_chunk_size):
            batch = chunk_items[i:i + self.batch_insert_chunk_size]
            tasks.append(process_batch(batch))
        
        # 并发处理所有批次
        await asyncio.gather(*tasks)

    async def _extract_entities_in_batches(self, inserting_chunks):
        """并发处理实体抽取（带简单进度显示）"""
        from .operate import extract_entities
        
        logger.info(f"[批量实体抽取] 并发处理 {len(inserting_chunks)} 个文本块（带进度显示）")
        
        return await extract_entities(
            inserting_chunks,
            knowledge_graph_inst=self.chunk_entity_relation_graph,
            entity_vdb=self.entities_vdb,
            relationships_vdb=self.relationships_vdb,
            global_config=asdict(self),
            show_progress=True,
            use_chinese_progress=True,
        )

    async def _insert_done(self):
        tasks = []
        for storage_inst in [
            self.full_docs,
            self.text_chunks,
            self.llm_response_cache,
            self.entities_vdb,
            self.relationships_vdb,
            self.chunks_vdb,
            self.chunk_entity_relation_graph,
        ]:
            if storage_inst is None:
                continue
            tasks.append(cast(StorageNameSpace, storage_inst).index_done_callback())
        await asyncio.gather(*tasks)

    def insert_custom_kg(self, custom_kg: dict):
        loop = always_get_an_event_loop()
        return loop.run_until_complete(self.ainsert_custom_kg(custom_kg))

    async def ainsert_custom_kg(self, custom_kg: dict):
        update_storage = False
        try:

            all_chunks_data = {}
            chunk_to_source_map = {}
            for chunk_data in custom_kg.get("chunks", []):
                chunk_content = chunk_data["content"]
                source_id = chunk_data["source_id"]
                chunk_id = compute_mdhash_id(chunk_content.strip(), prefix="chunk-")

                chunk_entry = {"content": chunk_content.strip(), "source_id": source_id}
                all_chunks_data[chunk_id] = chunk_entry
                chunk_to_source_map[source_id] = chunk_id
                update_storage = True

            if self.chunks_vdb is not None and all_chunks_data:
                await self.chunks_vdb.upsert(all_chunks_data)
            if self.text_chunks is not None and all_chunks_data:
                await self.text_chunks.upsert(all_chunks_data)

 
            all_entities_data = []
            for entity_data in custom_kg.get("entities", []):
                entity_name = f'"{entity_data["entity_name"].upper()}"'
                entity_type = entity_data.get("entity_type", "UNKNOWN")
                description = entity_data.get("description", "No description provided")

                source_chunk_id = entity_data.get("source_id", "UNKNOWN")
                source_id = chunk_to_source_map.get(source_chunk_id, "UNKNOWN")


                if source_id == "UNKNOWN":
                    logger.warning(
                        f"Entity '{entity_name}' has an UNKNOWN source_id. Please check the source mapping."
                    )


                node_data = {
                    "entity_type": entity_type,
                    "description": description,
                    "source_id": source_id,
                }

                await self.chunk_entity_relation_graph.upsert_node(
                    entity_name, node_data=node_data
                )
                node_data["entity_name"] = entity_name
                all_entities_data.append(node_data)
                update_storage = True


            all_relationships_data = []
            for relationship_data in custom_kg.get("relationships", []):
                src_id = f'"{relationship_data["src_id"].upper()}"'
                tgt_id = f'"{relationship_data["tgt_id"].upper()}"'
                description = relationship_data["description"]
                keywords = relationship_data["keywords"]
                weight = relationship_data.get("weight", 1.0)

                source_chunk_id = relationship_data.get("source_id", "UNKNOWN")
                source_id = chunk_to_source_map.get(source_chunk_id, "UNKNOWN")


                if source_id == "UNKNOWN":
                    logger.warning(
                        f"Relationship from '{src_id}' to '{tgt_id}' has an UNKNOWN source_id. Please check the source mapping."
                    )


                for need_insert_id in [src_id, tgt_id]:
                    if not (
                        await self.chunk_entity_relation_graph.has_node(need_insert_id)
                    ):
                        await self.chunk_entity_relation_graph.upsert_node(
                            need_insert_id,
                            node_data={
                                "source_id": source_id,
                                "description": "UNKNOWN",
                                "entity_type": "UNKNOWN",
                            },
                        )


                await self.chunk_entity_relation_graph.upsert_edge(
                    src_id,
                    tgt_id,
                    edge_data={
                        "weight": weight,
                        "description": description,
                        "keywords": keywords,
                        "source_id": source_id,
                    },
                )
                edge_data = {
                    "src_id": src_id,
                    "tgt_id": tgt_id,
                    "description": description,
                    "keywords": keywords,
                }
                all_relationships_data.append(edge_data)
                update_storage = True


            if self.entities_vdb is not None:
                data_for_vdb = {
                    compute_mdhash_id(dp["entity_name"], prefix="ent-"): {
                        "content": dp["entity_name"] + dp["description"],
                        "entity_name": dp["entity_name"],
                    }
                    for dp in all_entities_data
                }
                await self.entities_vdb.upsert(data_for_vdb)


            if self.relationships_vdb is not None:
                data_for_vdb = {
                    compute_mdhash_id(dp["src_id"] + dp["tgt_id"], prefix="rel-"): {
                        "src_id": dp["src_id"],
                        "tgt_id": dp["tgt_id"],
                        "content": dp["keywords"]
                        + dp["src_id"]
                        + dp["tgt_id"]
                        + dp["description"],
                    }
                    for dp in all_relationships_data
                }
                await self.relationships_vdb.upsert(data_for_vdb)
        finally:
            if update_storage:
                await self._insert_done()
    
    def query(self, query: str, param: QueryParam = QueryParam(), use_cache: bool = True):
        loop = always_get_an_event_loop()
        return loop.run_until_complete(self.aquery(query, param, use_cache))
    
    async def aquery(self, query: str, param: QueryParam = QueryParam(), use_cache: bool = True):
        if param.mode in ["hybrid"]:
            response= await kg_query(
                query,
                self.chunk_entity_relation_graph,
                self.entities_vdb,
                self.relationships_vdb,
                self.text_chunks,
                param,
                asdict(self),
                hashing_kv=self.llm_response_cache
                if self.llm_response_cache
                and hasattr(self.llm_response_cache, "global_config")
                else self.key_string_value_json_storage_cls(
                    global_config=asdict(self),
                ),
                use_cache=use_cache,
            )
            print("response all ready")
        else:
            raise ValueError(f"Unknown mode {param.mode}")
        await self._query_done()
        return response

    def query_with_keywords(self, keywords: list[str], param: QueryParam = QueryParam()):
        """
        基于关键词列表进行查询
        
        Args:
            keywords: 关键词列表
            param: 查询参数（包含use_path_retrieval等所有查询选项）
            
        Returns:
            str: 格式化的上下文文本（标准模式）
            dict: 包含上下文和文档列表的字典（结构化模式或路径检索模式）
        """
        loop = always_get_an_event_loop()
        return loop.run_until_complete(self.aquery_with_keywords(keywords, param))
    
    async def aquery_with_keywords(self, keywords: list[str], param: QueryParam = QueryParam()):
        """
        基于关键词列表进行异步查询
        
        Args:
            keywords: 关键词列表
            param: 查询参数（包含use_path_retrieval等所有查询选项）
            
        Returns:
            查询结果（格式取决于参数设置）
        """
        from .operate import kg_query_by_keywords
        
        if param.mode in ["hybrid"]:
            response = await kg_query_by_keywords(
                keywords=keywords,
                knowledge_graph_inst=self.chunk_entity_relation_graph,
                entities_vdb=self.entities_vdb,
                relationships_vdb=self.relationships_vdb,
                text_chunks_db=self.text_chunks,
                query_param=param,
                global_config=asdict(self),
            )
            print("keyword query response ready")
        else:
            raise ValueError(f"Unknown mode {param.mode}")
        
        await self._query_done()
        return response
        
    async def _query_done(self):
        tasks = []
        for storage_inst in [self.llm_response_cache]:
            if storage_inst is None:
                continue
            tasks.append(cast(StorageNameSpace, storage_inst).index_done_callback())
        await asyncio.gather(*tasks)

    def delete_by_entity(self, entity_name: str):
        loop = always_get_an_event_loop()
        return loop.run_until_complete(self.adelete_by_entity(entity_name))

    async def adelete_by_entity(self, entity_name: str):
        entity_name = f'"{entity_name.upper()}"'

        try:
            await self.entities_vdb.delete_entity(entity_name)
            await self.relationships_vdb.delete_relation(entity_name)
            await self.chunk_entity_relation_graph.delete_node(entity_name)

            logger.info(
                f"Entity '{entity_name}' and its relationships have been deleted."
            )
            await self._delete_by_entity_done()
        except Exception as e:
            logger.error(f"Error while deleting entity '{entity_name}': {e}")

    async def _delete_by_entity_done(self):
        tasks = []
        for storage_inst in [
            self.entities_vdb,
            self.relationships_vdb,
            self.chunk_entity_relation_graph,
        ]:
            if storage_inst is None:
                continue
            tasks.append(cast(StorageNameSpace, storage_inst).index_done_callback())
        await asyncio.gather(*tasks)
