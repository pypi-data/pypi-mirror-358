import asyncio
import json
import re
from tqdm.asyncio import tqdm as tqdm_async
from typing import Union
from collections import Counter, defaultdict
import warnings
import tiktoken
import time
import csv
from .utils import (
    logger,
    clean_str,
    compute_mdhash_id,
    decode_tokens_by_tiktoken,
    encode_string_by_tiktoken,
    is_float_regex,
    list_of_list_to_csv,
    pack_user_ass_to_openai_messages,
    split_string_by_multi_markers,
    truncate_list_by_token_size,
    process_combine_contexts,
    compute_args_hash,
    handle_cache,
    save_to_cache,
    CacheData,
)
from .base import (
    BaseGraphStorage,
    BaseKVStorage,
    BaseVectorStorage,
    TextChunkSchema,
    QueryParam,
)
from .prompt import GRAPH_FIELD_SEP, PROMPTS


def chunking_by_token_size(
    content: str, overlap_token_size=128, max_token_size=1024, tiktoken_model="gpt-4o"
):
    tokens = encode_string_by_tiktoken(content, model_name=tiktoken_model)
    results = []
    for index, start in enumerate(
        range(0, len(tokens), max_token_size - overlap_token_size)
    ):
        chunk_content = decode_tokens_by_tiktoken(
            tokens[start : start + max_token_size], model_name=tiktoken_model
        )
        results.append(
            {
                "tokens": min(max_token_size, len(tokens) - start),
                "content": chunk_content.strip(),
                "chunk_order_index": index,
            }
        )
    return results


async def _handle_entity_relation_summary(
    entity_or_relation_name: str,
    description: str,
    global_config: dict,
) -> str:
    use_llm_func: callable = global_config["llm_model_func"]
    llm_max_tokens = global_config["llm_model_max_token_size"]
    tiktoken_model_name = global_config["tiktoken_model_name"]
    summary_max_tokens = global_config["entity_summary_to_max_tokens"]
    language = global_config["addon_params"].get(
        "language", PROMPTS["DEFAULT_LANGUAGE"]
    )

    tokens = encode_string_by_tiktoken(description, model_name=tiktoken_model_name)
    if len(tokens) < summary_max_tokens: 
        return description
    prompt_template = PROMPTS["summarize_entity_descriptions"]
    use_description = decode_tokens_by_tiktoken(
        tokens[:llm_max_tokens], model_name=tiktoken_model_name
    )
    context_base = dict(
        entity_name=entity_or_relation_name,
        description_list=use_description.split(GRAPH_FIELD_SEP),
        language=language,
    )
    use_prompt = prompt_template.format(**context_base)
    logger.debug(f"Trigger summary: {entity_or_relation_name}")
    summary = await use_llm_func(use_prompt, max_tokens=summary_max_tokens)
    return summary


async def _handle_single_entity_extraction(
    record_attributes: list[str],
    chunk_key: str,
):
    if len(record_attributes) < 4 or record_attributes[0] != '"entity"':
        return None
   
    entity_name = clean_str(record_attributes[1].upper())
    if not entity_name.strip():
        return None
    entity_type = clean_str(record_attributes[2].upper())
    entity_description = clean_str(record_attributes[3])
    entity_source_id = chunk_key
    return dict(
        entity_name=entity_name,
        entity_type=entity_type,
        description=entity_description,
        source_id=entity_source_id,
    )


async def _handle_single_relationship_extraction(
    record_attributes: list[str],
    chunk_key: str,
):
    if len(record_attributes) < 5 or record_attributes[0] != '"relationship"':
        return None
   
    source = clean_str(record_attributes[1].upper())
    target = clean_str(record_attributes[2].upper())
    edge_description = clean_str(record_attributes[3])

    edge_keywords = clean_str(record_attributes[4])
    edge_source_id = chunk_key
    weight = (
        float(record_attributes[-1]) if is_float_regex(record_attributes[-1]) else 1.0
    )
    return dict(
        src_id=source,
        tgt_id=target,
        weight=weight,
        description=edge_description,
        keywords=edge_keywords,
        source_id=edge_source_id,
    )


async def _merge_nodes_then_upsert(
    entity_name: str,
    nodes_data: list[dict],
    knowledge_graph_inst: BaseGraphStorage,
    global_config: dict,
):
    already_entity_types = []
    already_source_ids = []
    already_description = []

    already_node = await knowledge_graph_inst.get_node(entity_name)
    if already_node is not None:
        already_entity_types.append(already_node["entity_type"])
        already_source_ids.extend(
            split_string_by_multi_markers(already_node["source_id"], [GRAPH_FIELD_SEP])
        )
        already_description.append(already_node["description"])

    entity_type = sorted(
        Counter(
            [dp["entity_type"] for dp in nodes_data] + already_entity_types
        ).items(),
        key=lambda x: x[1],
        reverse=True,
    )[0][0]
    description = GRAPH_FIELD_SEP.join(
        sorted(set([dp["description"] for dp in nodes_data] + already_description))
    )
    source_id = GRAPH_FIELD_SEP.join(
        set([dp["source_id"] for dp in nodes_data] + already_source_ids)
    )
    description = await _handle_entity_relation_summary(
        entity_name, description, global_config
    )
    node_data = dict(
        entity_type=entity_type,
        description=description,
        source_id=source_id,
    )
    await knowledge_graph_inst.upsert_node(
        entity_name,
        node_data=node_data,
    )
    node_data["entity_name"] = entity_name
    return node_data


async def _merge_edges_then_upsert(
    src_id: str,
    tgt_id: str,
    edges_data: list[dict],
    knowledge_graph_inst: BaseGraphStorage,
    global_config: dict,
):
    already_weights = []
    already_source_ids = []
    already_description = []
    already_keywords = []

    if await knowledge_graph_inst.has_edge(src_id, tgt_id):
        already_edge = await knowledge_graph_inst.get_edge(src_id, tgt_id)
        already_weights.append(already_edge["weight"])
        already_source_ids.extend(
            split_string_by_multi_markers(already_edge["source_id"], [GRAPH_FIELD_SEP])
        )
        already_description.append(already_edge["description"])
        already_keywords.extend(
            split_string_by_multi_markers(already_edge["keywords"], [GRAPH_FIELD_SEP])
        )

    weight = sum([dp["weight"] for dp in edges_data] + already_weights)
    description = GRAPH_FIELD_SEP.join(
        sorted(set([dp["description"] for dp in edges_data] + already_description))
    )
    keywords = GRAPH_FIELD_SEP.join(
        sorted(set([dp["keywords"] for dp in edges_data] + already_keywords))
    )
    source_id = GRAPH_FIELD_SEP.join(
        set([dp["source_id"] for dp in edges_data] + already_source_ids)
    )
    for need_insert_id in [src_id, tgt_id]:
        if not (await knowledge_graph_inst.has_node(need_insert_id)):
            await knowledge_graph_inst.upsert_node(
                need_insert_id,
                node_data={
                    "source_id": source_id,
                    "description": description,
                    "entity_type": '"UNKNOWN"',
                },
            )
    description = await _handle_entity_relation_summary(
        f"({src_id}, {tgt_id})", description, global_config
    )
    await knowledge_graph_inst.upsert_edge(
        src_id,
        tgt_id,
        edge_data=dict(
            weight=weight,
            description=description,
            keywords=keywords,
            source_id=source_id,
        ),
    )

    edge_data = dict(
        src_id=src_id,
        tgt_id=tgt_id,
        description=description,
        keywords=keywords,
    )

    return edge_data


class SimpleProgress:
    """简单的线程安全进度计数器"""
    def __init__(self, use_chinese=True):
        self._lock = asyncio.Lock()
        self.processed = 0
        self.entities = 0
        self.relations = 0
        self.use_chinese = use_chinese
    
    async def update(self, processed_inc=0, entities_inc=0, relations_inc=0):
        async with self._lock:
            self.processed += processed_inc
            self.entities += entities_inc
            self.relations += relations_inc
            
            # 显示进度
            ticks = PROMPTS["process_tickers"][self.processed % len(PROMPTS["process_tickers"])]
            if self.use_chinese:
                progress_text = f"{ticks} 已处理 {self.processed} 个文本块, 发现 {self.entities} 个实体, {self.relations} 个关系\r"
            else:
                progress_text = f"{ticks} Processed {self.processed} chunks, {self.entities} entities, {self.relations} relations\r"
            
            print(progress_text, end="", flush=True)


async def extract_entities(
    chunks: dict[str, TextChunkSchema],
    knowledge_graph_inst: BaseGraphStorage,
    entity_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    global_config: dict,
    show_progress: bool = True,
    use_chinese_progress: bool = False,
) -> Union[BaseGraphStorage, None]:
    time.sleep(20)
    use_llm_func: callable = global_config["llm_model_func"]
    entity_extract_max_gleaning = global_config["entity_extract_max_gleaning"]

    ordered_chunks = list(chunks.items())
  
    language = global_config["addon_params"].get(
        "language", PROMPTS["DEFAULT_LANGUAGE"]
    )
    entity_types = global_config["addon_params"].get(
        "entity_types", PROMPTS["DEFAULT_ENTITY_TYPES"]
    )
    example_number = global_config["addon_params"].get("example_number", None)
    if example_number and example_number < len(PROMPTS["entity_extraction_examples"]):
        examples = "\n".join(
            PROMPTS["entity_extraction_examples"][: int(example_number)]
        )
    else:
        examples = "\n".join(PROMPTS["entity_extraction_examples"])

    example_context_base = dict(
        tuple_delimiter=PROMPTS["DEFAULT_TUPLE_DELIMITER"],
        record_delimiter=PROMPTS["DEFAULT_RECORD_DELIMITER"],
        completion_delimiter=PROMPTS["DEFAULT_COMPLETION_DELIMITER"],
        entity_types=",".join(entity_types),
        language=language,
    )
  
    examples = examples.format(**example_context_base)

    entity_extract_prompt = PROMPTS["entity_extraction"]
    context_base = dict(
        tuple_delimiter=PROMPTS["DEFAULT_TUPLE_DELIMITER"],
        record_delimiter=PROMPTS["DEFAULT_RECORD_DELIMITER"],
        completion_delimiter=PROMPTS["DEFAULT_COMPLETION_DELIMITER"],
        entity_types=",".join(entity_types),
        examples=examples,
        language=language,
    )

    continue_prompt = PROMPTS["entiti_continue_extraction"]
    if_loop_prompt = PROMPTS["entiti_if_loop_extraction"]

    # 线程安全的进度计数器（如果启用进度显示）
    progress = SimpleProgress(use_chinese=use_chinese_progress) if show_progress else None

    async def _process_single_content(chunk_key_dp: tuple[str, TextChunkSchema]):
        chunk_key = chunk_key_dp[0]
        chunk_dp = chunk_key_dp[1]
        content = chunk_dp["content"]
        
        try:
            hint_prompt = entity_extract_prompt.format(
                **context_base, input_text="{input_text}"
            ).format(**context_base, input_text=content)

            final_result = await use_llm_func(hint_prompt)
            history = pack_user_ass_to_openai_messages(hint_prompt, final_result)
            
            for now_glean_index in range(entity_extract_max_gleaning):
                glean_result = await use_llm_func(continue_prompt, history_messages=history)
                history += pack_user_ass_to_openai_messages(continue_prompt, glean_result)
                final_result += glean_result
                
                if now_glean_index == entity_extract_max_gleaning - 1:
                    break

                if_loop_result: str = await use_llm_func(
                    if_loop_prompt, history_messages=history
                )
                if_loop_result = if_loop_result.strip().strip('"').strip("'").lower()
                if if_loop_result != "yes":
                    break

            records = split_string_by_multi_markers(
                final_result,
                [context_base["record_delimiter"], context_base["completion_delimiter"]],
            )

            maybe_nodes = defaultdict(list)
            maybe_edges = defaultdict(list)
            
            for record in records:
                record_match = re.search(r"\((.*)\)", record)
                if record_match is None:
                    continue
                record = record_match.group(1)
                record_attributes = split_string_by_multi_markers(
                    record, [context_base["tuple_delimiter"]]
                )
                
                if_entities = await _handle_single_entity_extraction(
                    record_attributes, chunk_key
                )
                if if_entities is not None:
                    maybe_nodes[if_entities["entity_name"]].append(if_entities)
                    continue

                if_relation = await _handle_single_relationship_extraction(
                    record_attributes, chunk_key
                )
                if if_relation is not None:
                    maybe_edges[(if_relation["src_id"], if_relation["tgt_id"])].append(
                        if_relation
                    )
            
            # 线程安全地更新进度（如果启用进度显示）
            if progress:
                await progress.update(
                    processed_inc=1,
                    entities_inc=len(maybe_nodes),
                    relations_inc=len(maybe_edges)
                )
            
            return dict(maybe_nodes), dict(maybe_edges)
            
        except Exception as e:
            logger.error(f"处理文本块 {chunk_key} 时出错: {e}")
            if progress:
                await progress.update(processed_inc=1)  # 即使出错也要更新计数
            return {}, {}

    # 并发处理所有chunks
    results = []
    if show_progress:
        desc_text = "提取实体" if use_chinese_progress else "Extracting entities from chunks"
        unit_text = "文本块" if use_chinese_progress else "chunk"
    else:
        desc_text = "Extracting entities from chunks"
        unit_text = "chunk"
        
    for result in tqdm_async(
        asyncio.as_completed([_process_single_content(c) for c in ordered_chunks]),
        total=len(ordered_chunks),
        desc=desc_text,
        unit=unit_text,
    ):
        results.append(await result)

    if show_progress:
        print()  # 换行，结束进度显示

    # 合并结果
    maybe_nodes = defaultdict(list)
    maybe_edges = defaultdict(list)
    for m_nodes, m_edges in results:
        for k, v in m_nodes.items():
            maybe_nodes[k].extend(v)
        for k, v in m_edges.items():
            maybe_edges[k].extend(v)
            
    # 插入实体到存储
    if use_chinese_progress:
        logger.info("正在插入实体到存储...")
    else:
        logger.info("Inserting entities into storage...")
    all_entities_data = []
    
    entity_desc = "插入实体" if use_chinese_progress else "Inserting entities"
    entity_unit = "实体" if use_chinese_progress else "entity"
    
    for result in tqdm_async(
        asyncio.as_completed(
            [
                _merge_nodes_then_upsert(k, v, knowledge_graph_inst, global_config)
                for k, v in maybe_nodes.items()
            ]
        ),
        total=len(maybe_nodes),
        desc=entity_desc,
        unit=entity_unit,
    ):
        all_entities_data.append(await result)

    # 插入关系到存储
    if use_chinese_progress:
        logger.info("正在插入关系到存储...")
    else:
        logger.info("Inserting relationships into storage...")
    all_relationships_data = []
    
    relation_desc = "插入关系" if use_chinese_progress else "Inserting relationships"
    relation_unit = "关系" if use_chinese_progress else "relationship"
    
    for result in tqdm_async(
        asyncio.as_completed(
            [
                _merge_edges_then_upsert(
                    k[0], k[1], v, knowledge_graph_inst, global_config
                )
                for k, v in maybe_edges.items()
            ]
        ),
        total=len(maybe_edges),
        desc=relation_desc,
        unit=relation_unit,
    ):
        all_relationships_data.append(await result)

    if not len(all_entities_data) and not len(all_relationships_data):
        logger.warning(
            "Didn't extract any entities and relationships, maybe your LLM is not working"
        )
        return None

    if not len(all_entities_data):
        logger.warning("Didn't extract any entities")
    if not len(all_relationships_data):
        logger.warning("Didn't extract any relationships")

    if entity_vdb is not None:
        data_for_vdb = {
            compute_mdhash_id(dp["entity_name"], prefix="ent-"): {
                "content": dp["entity_name"] + dp["description"],
                "entity_name": dp["entity_name"],
            }
            for dp in all_entities_data
        }
        await entity_vdb.upsert(data_for_vdb)

    if relationships_vdb is not None:
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
        await relationships_vdb.upsert(data_for_vdb)

    return knowledge_graph_inst



async def _kg_query_core(
    ll_keywords: str,
    hl_keywords: str,
    original_query: str,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
    global_config: dict,
    use_cache: bool = True,
    hashing_kv: BaseKVStorage = None,
    use_path_retrieval: bool = False,
) -> Union[str, dict]:
    """
    知识图谱查询核心函数 - 包含除关键词提取外的所有查询逻辑
    
    Args:
        ll_keywords: 低级关键词（逗号分隔的字符串）
        hl_keywords: 高级关键词（逗号分隔的字符串）
        original_query: 原始查询（用于缓存和提示词）
        knowledge_graph_inst: 知识图谱存储实例
        entities_vdb: 实体向量数据库
        relationships_vdb: 关系向量数据库
        text_chunks_db: 文本块数据库
        query_param: 查询参数
        global_config: 全局配置
        use_cache: 是否使用缓存
        hashing_kv: 缓存存储实例
        use_path_retrieval: 是否使用路径检索模式
    
    Returns:
        查询结果（字符串或字典，取决于查询参数）
    """
    use_model_func = global_config["llm_model_func"]
    
    # ==================== 缓存检查 ====================
    cached_response, quantized, min_val, max_val = None, None, None, None
    args_hash = None
    
    if use_cache and hashing_kv is not None:
        args_hash = compute_args_hash(query_param.mode, original_query)
        cached_response, quantized, min_val, max_val = await handle_cache(
            hashing_kv, args_hash, original_query, query_param.mode
        )
        if cached_response is not None:
            logger.info("返回缓存结果")
            return cached_response

    # ==================== 验证查询模式 ====================
    if query_param.mode not in ["hybrid"]:
        error_msg = f"不支持的查询模式: {query_param.mode}"
        logger.error(error_msg)
        if use_path_retrieval:
            return {
                "context": error_msg,
                "documents": [],
                "path_entities": [],
                "path_connections": [],
                "statistics": {"total_entities": 0, "total_connections": 0, "total_documents": 0},
                "mode": "keyword_path_retrieval"
            }
        return PROMPTS["fail_response"]

    # ==================== 验证关键词 ====================
    if ll_keywords == "" and hl_keywords == "":
        error_msg = "高级和低级关键词都为空"
        logger.warning(error_msg)
        if use_path_retrieval:
            return {
                "context": error_msg,
                "documents": [],
                "path_entities": [],
                "path_connections": [],
                "statistics": {"total_entities": 0, "total_connections": 0, "total_documents": 0},
                "mode": "keyword_path_retrieval"
            }
        return PROMPTS["fail_response"]

    # ==================== 构建上下文 ====================
    if use_path_retrieval:
        # 路径检索模式：专注于关键词之间的连接路径
        keywords_str = ll_keywords if ll_keywords else hl_keywords
        logger.info("使用路径检索模式")
        path_data = await _build_query_context_for_path(
            keywords_str,
            knowledge_graph_inst,
            entities_vdb,
            relationships_vdb,
            text_chunks_db,
            query_param,
        )
        
        # 路径检索模式总是返回结构化结果
        return {
            "context": path_data["formatted_context"],
            "documents": path_data["documents"],
            "path_entities": path_data["path_entities"],
            "path_connections": path_data["path_connections"],
            "statistics": path_data["statistics"],
            "mode": "keyword_path_retrieval"
        }
    else:
        # 标准模式：使用高级/低级关键词方式
        keywords = [ll_keywords, hl_keywords]
        
        # 根据返回需求选择不同的上下文构建方式
        if query_param.return_context_and_answer:
            context_data = await _build_query_context_structured(
                keywords,
                knowledge_graph_inst,
                entities_vdb,
                relationships_vdb,
                text_chunks_db,
                query_param,
            )
            context = context_data["formatted_context"]
            documents = context_data["documents"]
        else:
            context = await _build_query_context(
                keywords,
                knowledge_graph_inst,
                entities_vdb,
                relationships_vdb,
                text_chunks_db,
                query_param,
            )
            documents = None

        # 如果只需要上下文，直接返回
        if query_param.only_need_context:
            return context
        
        # 验证上下文构建是否成功
        if context is None:
            logger.error("上下文构建失败")
            return PROMPTS["fail_response"]

        # ==================== 生成答案 ====================
        sys_prompt_temp = PROMPTS["rag_response"]
        sys_prompt = sys_prompt_temp.format(
            context_data=context, response_type=query_param.response_type
        )
        
        if query_param.only_need_prompt:
            return sys_prompt
        
        response = await use_model_func(
            original_query,
            system_prompt=sys_prompt,
            stream=query_param.stream,
        )
        
        # 清理LLM响应
        if isinstance(response, str) and len(response) > len(sys_prompt):
            response = (
                response.replace(sys_prompt, "")
                .replace("user", "")
                .replace("model", "")
                .replace(original_query, "")
                .replace("<s>", "")
                .replace("</s>", "")
                .strip()
            )

        # ==================== 保存缓存和返回结果 ====================
        # 保存缓存
        if use_cache and hashing_kv is not None and args_hash is not None:
            await save_to_cache(
                hashing_kv,
                CacheData(
                    args_hash=args_hash,
                    content=response,
                    prompt=original_query,
                    quantized=quantized,
                    min_val=min_val,
                    max_val=max_val,
                    mode=query_param.mode,
                ),
            )

        # 返回结果
        if query_param.return_context_and_answer:
            return {
                "answer": response,
                "context": context,
                "documents": documents
            }
        else:
            return response


async def kg_query(
    query,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
    global_config: dict,
    hashing_kv: BaseKVStorage = None,
    use_cache: bool = True,
) -> Union[str, dict]:
    """
    知识图谱查询主函数 - PathRAG核心查询流程
    
    主要流程：
    1. 缓存检查 - 检查是否有已缓存的结果
    2. 关键词提取 - 使用LLM提取高级和低级关键词
    3. 上下文构建 - 基于关键词从知识图谱中检索相关信息
    4. 答案生成 - 使用LLM基于上下文生成最终答案
    5. 结果返回 - 根据参数返回不同格式的结果
    6. 缓存保存 - 保存结果到缓存以便后续使用
    """

    # ==================== 步骤1: 初始化和缓存检查 ====================
    use_model_func = global_config["llm_model_func"]
    args_hash = compute_args_hash(query_param.mode, query)
    
    # 检查缓存 - 如果启用缓存且有已缓存结果，直接返回
    cached_response, quantized, min_val, max_val = None, None, None, None
    if use_cache:
        cached_response, quantized, min_val, max_val = await handle_cache(
            hashing_kv, args_hash, query, query_param.mode
        )
        if cached_response is not None:
            logger.info("返回缓存结果")
            return cached_response

    # ==================== 步骤2: 关键词提取准备 ====================
    # 配置关键词提取的示例数量和语言
    example_number = global_config["addon_params"].get("example_number", None)
    if example_number and example_number < len(PROMPTS["keywords_extraction_examples"]):
        examples = "\n".join(
            PROMPTS["keywords_extraction_examples"][: int(example_number)]
        )
    else:
        examples = "\n".join(PROMPTS["keywords_extraction_examples"])
    language = global_config["addon_params"].get(
        "language", PROMPTS["DEFAULT_LANGUAGE"]
    )

    # 验证查询模式
    if query_param.mode not in ["hybrid"]:
        logger.error(f"Unknown mode {query_param.mode} in kg_query")
        return PROMPTS["fail_response"]

    # ==================== 步骤3: 使用LLM提取关键词 ====================
    # 构建关键词提取的提示词
    kw_prompt_temp = PROMPTS["keywords_extraction"]
    kw_prompt = kw_prompt_temp.format(query=query, examples=examples, language=language)
    
    # 调用LLM提取关键词
    result = await use_model_func(kw_prompt, keyword_extraction=True)
    logger.info("关键词提取结果:")
    print(result)
    
    # ==================== 步骤4: 解析关键词提取结果 ====================
    try:
        # 使用正则表达式提取JSON格式的结果
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            result = match.group(0)
            keywords_data = json.loads(result)

            # 提取高级关键词（用于全局/关系查询）和低级关键词（用于局部/实体查询）
            hl_keywords = keywords_data.get("high_level_keywords", [])  # 高级关键词
            ll_keywords = keywords_data.get("low_level_keywords", [])   # 低级关键词
        else:
            logger.error("在LLM结果中未找到JSON格式的关键词")
            return PROMPTS["fail_response"]

    except json.JSONDecodeError as e:
        logger.error(f"关键词JSON解析错误: {e} {result}")
        return PROMPTS["fail_response"]

    # ==================== 步骤5: 验证和处理关键词 ====================
    # 检查是否成功提取到关键词
    if hl_keywords == [] and ll_keywords == []:
        logger.warning("高级和低级关键词都为空")
        return PROMPTS["fail_response"]
    
    # 在hybrid模式下，两种关键词都不能为空
    if ll_keywords == [] and query_param.mode in ["hybrid"]:
        logger.warning("低级关键词为空")
        return PROMPTS["fail_response"]
    else:
        ll_keywords = ", ".join(ll_keywords)  # 转换为逗号分隔的字符串
        
    if hl_keywords == [] and query_param.mode in ["hybrid"]:
        logger.warning("高级关键词为空")
        return PROMPTS["fail_response"]
    else:
        hl_keywords = ", ".join(hl_keywords)  # 转换为逗号分隔的字符串


    # ==================== 步骤6: 构建查询上下文 ====================
    keywords = [ll_keywords, hl_keywords]  # 组合关键词列表：[低级关键词, 高级关键词]
    
    # 根据返回需求选择不同的上下文构建方式
    if query_param.return_context_and_answer:
        # 需要同时返回上下文和答案时，使用结构化构建方式
        # 这种方式会额外收集原始文档列表，便于调试和分析
        context_data = await _build_query_context_structured(
            keywords,
            knowledge_graph_inst,
            entities_vdb,
            relationships_vdb,
            text_chunks_db,
            query_param,
        )
        context = context_data["formatted_context"]  # 格式化的上下文文本
        documents = context_data["documents"]        # 召回的原始文档列表
    else:
        # 标准模式：只构建格式化的上下文文本
        context = await _build_query_context(
            keywords,
            knowledge_graph_inst,
            entities_vdb,
            relationships_vdb,
            text_chunks_db,
            query_param,
        )
        documents = None

    # 如果只需要上下文，直接返回（用于调试或中间步骤查看）
    if query_param.only_need_context:
        return context
    
    # 验证上下文构建是否成功
    if context is None:
        logger.error("上下文构建失败")
        return PROMPTS["fail_response"]
    # ==================== 步骤7: 构建系统提示词并生成答案 ====================
    # 使用RAG响应模板构建系统提示词
    sys_prompt_temp = PROMPTS["rag_response"]
    sys_prompt = sys_prompt_temp.format(
        context_data=context, response_type=query_param.response_type
    )
    # 如果只需要提示词，直接返回（用于调试提示词构建）
    if query_param.only_need_prompt:
        return sys_prompt
    # 调用LLM生成最终答案
    response = await use_model_func(
        query,
        system_prompt=sys_prompt,
        stream=query_param.stream,
    )
    
    # ==================== 步骤8: 清理LLM响应 ====================
    # 移除响应中可能包含的系统提示词和其他无关内容
    if isinstance(response, str) and len(response) > len(sys_prompt):
        response = (
            response.replace(sys_prompt, "")
            .replace("user", "")
            .replace("model", "")
            .replace(query, "")
            .replace("<system>", "")
            .replace("</system>", "")
            .strip()
        )

    # ==================== 步骤9: 根据参数返回不同格式的结果 ====================
    # 如果需要同时返回上下文和答案
    if query_param.return_context_and_answer:
        # 返回结构化结果：包含答案、上下文和原始文档
        result = {
            "answer": response,      # LLM生成的最终答案
            "context": context,      # 格式化的上下文文本
            "documents": documents   # 召回的原始文档列表（用于调试和溯源）
        }
        # ==================== 步骤10: 保存缓存（结构化结果模式）====================
        if use_cache:
            # 注意：只缓存答案部分，不缓存整个结构化结果
            await save_to_cache(
                hashing_kv,
                CacheData(
                    args_hash=args_hash,
                    content=response,
                    prompt=query,
                    quantized=quantized,
                    min_val=min_val,
                    max_val=max_val,
                    mode=query_param.mode,
                ),
            )
        return result
    else:
        # ==================== 步骤10: 保存缓存（标准模式）====================
        # 标准模式：只返回答案字符串
        if use_cache:
            await save_to_cache(
                hashing_kv,
                CacheData(
                    args_hash=args_hash,
                    content=response,
                    prompt=query,
                    quantized=quantized,
                    min_val=min_val,
                    max_val=max_val,
                    mode=query_param.mode,
                ),
            )
        return response


async def kg_query_by_keywords(
    keywords: list[str],
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
    global_config: dict = {},
) -> dict:
    """
    基于关键词列表的知识图谱路径查询函数 - 重构后的简化版本
    
    与kg_query的主要区别：
    1. 输入是关键词列表，而不是自然语言问题
    2. 跳过LLM关键词提取步骤，直接使用提供的关键词
    3. 专门用于路径检索：查找关键词之间的连接路径和相关文档
    
    现在这个函数只负责：
    1. 关键词预处理（这是它独有的步骤）
    2. 调用核心查询函数（使用路径检索模式）
    """
    
    # ==================== 步骤1: 关键词预处理 ====================
    if not keywords:
        logger.warning("关键词列表为空")
        return {
            "context": "",
            "documents": [],
            "path_entities": [],
            "path_connections": [],
            "statistics": {"total_entities": 0, "total_connections": 0, "total_documents": 0},
            "mode": "keyword_path_retrieval"
        }
    
    # 将关键词列表合并为字符串
    keywords_str = ", ".join(keywords)
    logger.info(f"使用关键词: {keywords_str}")
    
    # ==================== 步骤2: 调用核心查询函数 ====================
    # 关键词查询总是使用路径检索模式
    return await _kg_query_core(
        ll_keywords=keywords_str,
        hl_keywords=keywords_str,
        original_query=f"关键词查询: {keywords_str}",
        knowledge_graph_inst=knowledge_graph_inst,
        entities_vdb=entities_vdb,
        relationships_vdb=relationships_vdb,
        text_chunks_db=text_chunks_db,
        query_param=query_param,
        global_config=global_config,
        use_cache=False,  # 关键词查询不使用缓存
        hashing_kv=None,
        use_path_retrieval=True,  # 关键词查询总是使用路径检索
    )


async def _build_query_context(
    query: list,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
):
    ll_entities_context, ll_relations_context, ll_text_units_context = "", "", ""
    hl_entities_context, hl_relations_context, hl_text_units_context = "", "", ""

    ll_kewwords, hl_keywrds = query[0], query[1]
    if query_param.mode in ["local", "hybrid"]:
        if ll_kewwords == "":
            ll_entities_context, ll_relations_context, ll_text_units_context = (
                "",
                "",
                "",
            )
            warnings.warn(
                "Low Level context is None. Return empty Low entity/relationship/source"
            )
            query_param.mode = "global"
        else:
            (
                ll_entities_context,
                ll_relations_context,
                ll_text_units_context,
            ) = await _get_node_data(
                ll_kewwords,
                knowledge_graph_inst,
                entities_vdb,
                text_chunks_db,
                query_param,
            )
    if query_param.mode in ["hybrid"]:
        if hl_keywrds == "":
            hl_entities_context, hl_relations_context, hl_text_units_context = (
                "",
                "",
                "",
            )
            warnings.warn(
                "High Level context is None. Return empty High entity/relationship/source"
            )
            query_param.mode = "local"
        else:
            (
                hl_entities_context,
                hl_relations_context,
                hl_text_units_context,
            ) = await _get_edge_data(
                hl_keywrds,
                knowledge_graph_inst,
                relationships_vdb,
                text_chunks_db,
                query_param,
            )
            if (
                hl_entities_context == ""
                and hl_relations_context == ""
                and hl_text_units_context == ""
            ):
                logger.warn("No high level context found. Switching to local mode.")
                query_param.mode = "local"
    if query_param.mode == "hybrid":
        entities_context, relations_context, text_units_context = combine_contexts(
            [hl_entities_context, hl_relations_context],
            [ll_entities_context, ll_relations_context],
            [hl_text_units_context, ll_text_units_context],
        )


    return f"""
-----global-information-----
-----high-level entity information-----
```csv
{hl_entities_context}
```
-----high-level relationship information-----
```csv
{hl_relations_context}
```
-----Sources-----
```csv
{text_units_context}
```
-----local-information-----
-----low-level entity information-----
```csv
{ll_entities_context}
```
-----low-level relationship information-----
```csv
{ll_relations_context}
```
"""


async def _build_query_context_structured(
    query: list,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
):
    """构建结构化的查询上下文，同时返回格式化上下文和原始文档列表"""
    ll_entities_context, ll_relations_context, ll_text_units_context = "", "", ""
    hl_entities_context, hl_relations_context, hl_text_units_context = "", "", ""
    
    # 收集所有文档
    all_documents = []

    ll_kewwords, hl_keywrds = query[0], query[1]
    if query_param.mode in ["local", "hybrid"]:
        if ll_kewwords == "":
            ll_entities_context, ll_relations_context, ll_text_units_context = (
                "",
                "",
                "",
            )
            warnings.warn(
                "Low Level context is None. Return empty Low entity/relationship/source"
            )
            query_param.mode = "global"
        else:
            (
                ll_entities_context,
                ll_relations_context,
                ll_text_units_context,
                ll_documents
            ) = await _get_node_data_with_docs(
                ll_kewwords,
                knowledge_graph_inst,
                entities_vdb,
                text_chunks_db,
                query_param,
            )
            all_documents.extend(ll_documents)
            
    if query_param.mode in ["hybrid"]:
        if hl_keywrds == "":
            hl_entities_context, hl_relations_context, hl_text_units_context = (
                "",
                "",
                "",
            )
            warnings.warn(
                "High Level context is None. Return empty High entity/relationship/source"
            )
            query_param.mode = "local"
        else:
            (
                hl_entities_context,
                hl_relations_context,
                hl_text_units_context,
                hl_documents
            ) = await _get_edge_data_with_docs(
                hl_keywrds,
                knowledge_graph_inst,
                relationships_vdb,
                text_chunks_db,
                query_param,
            )
            all_documents.extend(hl_documents)
            
    if query_param.mode == "hybrid":
        entities_context, relations_context, text_units_context = combine_contexts(
            [hl_entities_context, hl_relations_context],
            [ll_entities_context, ll_relations_context],
            [hl_text_units_context, ll_text_units_context],
        )

    # 去重文档（基于内容）
    unique_documents = []
    seen_content = set()
    for doc in all_documents:
        if doc["content"] not in seen_content:
            unique_documents.append(doc)
            seen_content.add(doc["content"])

    formatted_context = f"""
-----global-information-----
-----high-level entity information-----
```csv
{hl_entities_context}
```
-----high-level relationship information-----
```csv
{hl_relations_context}
```
-----Sources-----
```csv
{text_units_context}
```
-----local-information-----
-----low-level entity information-----
```csv
{ll_entities_context}
```
-----low-level relationship information-----
```csv
{ll_relations_context}
```
"""

    return {
        "formatted_context": formatted_context,
        "documents": unique_documents
    }


async def _build_query_context_for_path(
    keywords_str: str,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
):
    """
    专门用于路径检索的查询上下文构建函数 - 不区分高级和低级关键词
    
    专注于：
    1. 使用统一的关键词进行实体和关系查询
    2. 查找关键词之间的连接路径
    3. 收集路径相关的文档信息
    4. 返回路径导向的上下文
    
    Args:
        keywords_str: 关键词字符串（逗号分隔）
        其他参数与_build_query_context相同
        
    Returns:
        dict: 包含路径上下文和相关文档的字典
    """
    
    logger.info(f"路径检索模式 - 使用关键词: {keywords_str}")
    
    # ==================== 步骤1: 统一的实体查询 ====================
    # 使用统一的关键词查询相关实体
    entities_results = await entities_vdb.query(keywords_str, top_k=query_param.top_k)
    
    entity_names = []
    if entities_results:
        # 获取实体数据
        node_datas = await asyncio.gather(
            *[knowledge_graph_inst.get_node(r["entity_name"]) for r in entities_results]
        )
        
        # 获取实体度数（连接数）
        node_degrees = await asyncio.gather(
            *[knowledge_graph_inst.node_degree(r["entity_name"]) for r in entities_results]
        )
        
        # 组装实体数据
        entity_datas = [
            {**n, "entity_name": k["entity_name"], "rank": d}
            for k, n, d in zip(entities_results, node_datas, node_degrees)
            if n is not None
        ]
        
        entity_names = [e["entity_name"] for e in entity_datas]
        logger.info(f"找到相关实体: {len(entity_names)} 个")
    
    # ==================== 步骤2: 统一的关系查询 ====================
    # 使用统一的关键词查询相关关系
    relations_results = await relationships_vdb.query(keywords_str, top_k=query_param.top_k)
    
    path_edges = []
    path_entities_from_relations = set()
    
    if relations_results:
        # 获取关系数据
        edge_datas = await asyncio.gather(
            *[knowledge_graph_inst.get_edge(r["src_id"], r["tgt_id"]) for r in relations_results]
        )
        
        # 获取关系权重排序
        edge_degrees = await asyncio.gather(
            *[knowledge_graph_inst.edge_degree(r["src_id"], r["tgt_id"]) for r in relations_results]
        )
        
        # 过滤有效关系
        valid_edges = [
            {"src_id": k["src_id"], "tgt_id": k["tgt_id"], "rank": d, **v}
            for k, v, d in zip(relations_results, edge_datas, edge_degrees)
            if v is not None
        ]
        
        # 按权重排序
        path_edges = sorted(valid_edges, key=lambda x: (x["rank"], x.get("weight", 0)), reverse=True)
        
        # 收集路径中涉及的实体
        for edge in path_edges:
            path_entities_from_relations.add(edge["src_id"])
            path_entities_from_relations.add(edge["tgt_id"])
            
        logger.info(f"找到相关关系: {len(path_edges)} 个")
        logger.info(f"路径涉及实体: {len(path_entities_from_relations)} 个")
    
    # ==================== 步骤3: 合并和扩展实体集合 ====================
    # 合并从实体查询和关系查询得到的所有实体
    all_path_entities = set(entity_names) | path_entities_from_relations
    logger.info(f"总路径实体数: {len(all_path_entities)} 个")
    
    # ==================== 步骤4: 查找实体间的路径连接 ====================
    # 获取实体间的连接信息
    path_connections = []
    
    if len(all_path_entities) >= 2:
        # 查找实体之间的连接路径
        entity_list = list(all_path_entities)
        for i in range(len(entity_list)):
            for j in range(i + 1, len(entity_list)):
                src_entity = entity_list[i]
                tgt_entity = entity_list[j]
                
                # 检查是否存在直接连接
                try:
                    edge = await knowledge_graph_inst.get_edge(src_entity, tgt_entity)
                    if edge:
                        path_connections.append({
                            "src": src_entity,
                            "tgt": tgt_entity,
                            "edge_data": edge,
                            "connection_type": "direct"
                        })
                    else:
                        # 检查反向连接
                        reverse_edge = await knowledge_graph_inst.get_edge(tgt_entity, src_entity)
                        if reverse_edge:
                            path_connections.append({
                                "src": tgt_entity,
                                "tgt": src_entity,
                                "edge_data": reverse_edge,
                                "connection_type": "reverse"
                            })
                except Exception as e:
                    # 连接不存在或查询失败
                    continue
    
    logger.info(f"找到实体连接: {len(path_connections)} 个")
    
    # ==================== 步骤5: 收集路径相关的文档 ====================
    all_path_documents = []
    
    # 从实体查询获取文档
    if entities_results:
        entity_documents = await _find_most_related_text_unit_from_entities(
            entity_datas, query_param, text_chunks_db, knowledge_graph_inst
        )
        all_path_documents.extend(entity_documents)
    
    # 从关系查询获取文档
    if path_edges:
        relation_documents = await _find_related_text_unit_from_relationships(
            path_edges, query_param, text_chunks_db, knowledge_graph_inst
        )
        all_path_documents.extend(relation_documents)
    
    # ==================== 步骤6: 构建路径上下文 ====================
    # 构建实体信息
    entities_section_list = [["id", "entity", "type", "description", "relevance"]]
    for i, entity in enumerate(all_path_entities):
        try:
            entity_data = await knowledge_graph_inst.get_node(entity)
            if entity_data:
                entities_section_list.append([
                    i,
                    entity,
                    entity_data.get("entity_type", "UNKNOWN"),
                    entity_data.get("description", "UNKNOWN"),
                    "path_entity"
                ])
        except:
            entities_section_list.append([i, entity, "UNKNOWN", "UNKNOWN", "path_entity"])
    
    entities_context = list_of_list_to_csv(entities_section_list)
    
    # 构建路径连接信息
    connections_section_list = [["id", "source", "target", "description", "type"]]
    for i, conn in enumerate(path_connections):
        connections_section_list.append([
            i,
            conn["src"],
            conn["tgt"],
            conn["edge_data"].get("description", "UNKNOWN"),
            conn["connection_type"]
        ])
    
    connections_context = list_of_list_to_csv(connections_section_list)
    
    # 构建文档信息
    documents_section_list = [["id", "content"]]
    for i, doc in enumerate(all_path_documents):
        documents_section_list.append([i, doc["content"]])
    
    documents_context = list_of_list_to_csv(documents_section_list)
    
    # ==================== 步骤7: 去重文档 ====================
    unique_documents = []
    seen_content = set()
    for doc in all_path_documents:
        if doc["content"] not in seen_content:
            unique_documents.append(doc)
            seen_content.add(doc["content"])
    
    # ==================== 步骤8: 构建格式化的路径上下文 ====================
    formatted_context = f"""
-----路径检索结果-----
-----关键词-----
{keywords_str}

-----路径相关实体-----
```csv
{entities_context}
```

-----实体间连接路径-----
```csv
{connections_context}
```

-----路径相关文档-----
```csv
{documents_context}
```

-----路径统计信息-----
总实体数: {len(all_path_entities)}
总连接数: {len(path_connections)}
相关文档数: {len(unique_documents)}
"""

    logger.info(f"路径检索完成 - 实体:{len(all_path_entities)}, 连接:{len(path_connections)}, 文档:{len(unique_documents)}")
    
    return {
        "formatted_context": formatted_context,
        "documents": unique_documents,
        "path_entities": list(all_path_entities),
        "path_connections": path_connections,
        "statistics": {
            "total_entities": len(all_path_entities),
            "total_connections": len(path_connections),
            "total_documents": len(unique_documents)
        }
    }


async def _get_node_data(
    query,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
):

    results = await entities_vdb.query(query, top_k=query_param.top_k)
    if not len(results):
        return "", "", ""

    node_datas = await asyncio.gather(
        *[knowledge_graph_inst.get_node(r["entity_name"]) for r in results]
    )
    if not all([n is not None for n in node_datas]):
        logger.warning("Some nodes are missing, maybe the storage is damaged")


    node_degrees = await asyncio.gather(
        *[knowledge_graph_inst.node_degree(r["entity_name"]) for r in results]
    )
    node_datas = [
        {**n, "entity_name": k["entity_name"], "rank": d}
        for k, n, d in zip(results, node_datas, node_degrees)
        if n is not None
    ]  
    use_text_units = await _find_most_related_text_unit_from_entities(
        node_datas, query_param, text_chunks_db, knowledge_graph_inst
    )


    use_relations= await _find_most_related_edges_from_entities3(
        node_datas, query_param, knowledge_graph_inst
    )

    logger.info(
        f"Local query uses {len(node_datas)} entites, {len(use_relations)} relations, {len(use_text_units)} text units"
    )


    entites_section_list = [["id", "entity", "type", "description", "rank"]]
    for i, n in enumerate(node_datas):
        entites_section_list.append(
            [
                i,
                n["entity_name"],
                n.get("entity_type", "UNKNOWN"),
                n.get("description", "UNKNOWN"),
                n["rank"],
            ]
        )
    entities_context = list_of_list_to_csv(entites_section_list)

    relations_section_list=[["id","context"]]
    for i,e in enumerate(use_relations):
        relations_section_list.append([i,e])
    relations_context=list_of_list_to_csv(relations_section_list)

    text_units_section_list = [["id", "content"]]
    for i, t in enumerate(use_text_units):
        text_units_section_list.append([i, t["content"]])
    text_units_context = list_of_list_to_csv(text_units_section_list)
    
    return entities_context,relations_context,text_units_context


async def _get_node_data_with_docs(
    query,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
):
    """获取节点数据，同时返回原始文档列表"""
    results = await entities_vdb.query(query, top_k=query_param.top_k)
    if not len(results):
        return "", "", "", []

    node_datas = await asyncio.gather(
        *[knowledge_graph_inst.get_node(r["entity_name"]) for r in results]
    )
    if not all([n is not None for n in node_datas]):
        logger.warning("Some nodes are missing, maybe the storage is damaged")

    node_degrees = await asyncio.gather(
        *[knowledge_graph_inst.node_degree(r["entity_name"]) for r in results]
    )
    node_datas = [
        {**n, "entity_name": k["entity_name"], "rank": d}
        for k, n, d in zip(results, node_datas, node_degrees)
        if n is not None
    ]  
    use_text_units = await _find_most_related_text_unit_from_entities(
        node_datas, query_param, text_chunks_db, knowledge_graph_inst
    )

    use_relations= await _find_most_related_edges_from_entities3(
        node_datas, query_param, knowledge_graph_inst
    )

    logger.info(
        f"Local query uses {len(node_datas)} entites, {len(use_relations)} relations, {len(use_text_units)} text units"
    )

    entites_section_list = [["id", "entity", "type", "description", "rank"]]
    for i, n in enumerate(node_datas):
        entites_section_list.append(
            [
                i,
                n["entity_name"],
                n.get("entity_type", "UNKNOWN"),
                n.get("description", "UNKNOWN"),
                n["rank"],
            ]
        )
    entities_context = list_of_list_to_csv(entites_section_list)

    relations_section_list=[["id","context"]]
    for i,e in enumerate(use_relations):
        relations_section_list.append([i,e])
    relations_context=list_of_list_to_csv(relations_section_list)

    text_units_section_list = [["id", "content"]]
    for i, t in enumerate(use_text_units):
        text_units_section_list.append([i, t["content"]])
    text_units_context = list_of_list_to_csv(text_units_section_list)
    
    # 返回原始文档列表
    documents = use_text_units
    
    return entities_context, relations_context, text_units_context, documents


async def _find_most_related_text_unit_from_entities(
    node_datas: list[dict],
    query_param: QueryParam,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    knowledge_graph_inst: BaseGraphStorage,
):
    text_units = [
        split_string_by_multi_markers(dp["source_id"], [GRAPH_FIELD_SEP])
        for dp in node_datas
    ]
    edges = await asyncio.gather(
        *[knowledge_graph_inst.get_node_edges(dp["entity_name"]) for dp in node_datas]
    )
    all_one_hop_nodes = set()
    for this_edges in edges:
        if not this_edges:
            continue
        all_one_hop_nodes.update([e[1] for e in this_edges])

    all_one_hop_nodes = list(all_one_hop_nodes)
    all_one_hop_nodes_data = await asyncio.gather(
        *[knowledge_graph_inst.get_node(e) for e in all_one_hop_nodes]
    )


    all_one_hop_text_units_lookup = {
        k: set(split_string_by_multi_markers(v["source_id"], [GRAPH_FIELD_SEP]))
        for k, v in zip(all_one_hop_nodes, all_one_hop_nodes_data)
        if v is not None and "source_id" in v  
    }

    all_text_units_lookup = {}
    for index, (this_text_units, this_edges) in enumerate(zip(text_units, edges)):
        for c_id in this_text_units:
            if c_id not in all_text_units_lookup:
                all_text_units_lookup[c_id] = {
                    "data": await text_chunks_db.get_by_id(c_id),
                    "order": index,
                    "relation_counts": 0,
                }

            if this_edges:
                for e in this_edges:
                    if (
                        e[1] in all_one_hop_text_units_lookup
                        and c_id in all_one_hop_text_units_lookup[e[1]]
                    ):
                        all_text_units_lookup[c_id]["relation_counts"] += 1


    all_text_units = [
        {"id": k, **v}
        for k, v in all_text_units_lookup.items()
        if v is not None and v.get("data") is not None and "content" in v["data"]
    ]

    if not all_text_units:
        logger.warning("No valid text units found")
        return []

    all_text_units = sorted(
        all_text_units, key=lambda x: (x["order"], -x["relation_counts"])
    )

    all_text_units = truncate_list_by_token_size(
        all_text_units,
        key=lambda x: x["data"]["content"],
        max_token_size=query_param.max_token_for_text_unit,
    )

    all_text_units = [t["data"] for t in all_text_units]
    return all_text_units

async def _get_edge_data(
    keywords,
    knowledge_graph_inst: BaseGraphStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
):
    results = await relationships_vdb.query(keywords, top_k=query_param.top_k)

    if not len(results):
        return "", "", ""

    edge_datas = await asyncio.gather(
        *[knowledge_graph_inst.get_edge(r["src_id"], r["tgt_id"]) for r in results]
    )

    if not all([n is not None for n in edge_datas]):
        logger.warning("Some edges are missing, maybe the storage is damaged")
    edge_degree = await asyncio.gather(
        *[knowledge_graph_inst.edge_degree(r["src_id"], r["tgt_id"]) for r in results]
    )
    edge_datas = [
        {"src_id": k["src_id"], "tgt_id": k["tgt_id"], "rank": d, **v}
        for k, v, d in zip(results, edge_datas, edge_degree)
        if v is not None
    ]
    edge_datas = sorted(
        edge_datas, key=lambda x: (x["rank"], x["weight"]), reverse=True
    )
    edge_datas = truncate_list_by_token_size(
        edge_datas,
        key=lambda x: x["description"],
        max_token_size=query_param.max_token_for_global_context,
    )

    use_entities = await _find_most_related_entities_from_relationships(
        edge_datas, query_param, knowledge_graph_inst
    )
    use_text_units = await _find_related_text_unit_from_relationships(
        edge_datas, query_param, text_chunks_db, knowledge_graph_inst
    )
    logger.info(
        f"Global query uses {len(use_entities)} entites, {len(edge_datas)} relations, {len(use_text_units)} text units"
    )

    relations_section_list = [
        ["id", "source", "target", "description", "keywords", "weight", "rank"]
    ]
    for i, e in enumerate(edge_datas):
        relations_section_list.append(
            [
                i,
                e["src_id"],
                e["tgt_id"],
                e["description"],
                e["keywords"],
                e["weight"],
                e["rank"],
            ]
        )
    relations_context = list_of_list_to_csv(relations_section_list)

    entites_section_list = [["id", "entity", "type", "description", "rank"]]
    for i, n in enumerate(use_entities):
        entites_section_list.append(
            [
                i,
                n["entity_name"],
                n.get("entity_type", "UNKNOWN"),
                n.get("description", "UNKNOWN"),
                n["rank"],
            ]
        )
    entities_context = list_of_list_to_csv(entites_section_list)

    text_units_section_list = [["id", "content"]]
    for i, t in enumerate(use_text_units):
        text_units_section_list.append([i, t["content"]])
    text_units_context = list_of_list_to_csv(text_units_section_list)
    return entities_context, relations_context, text_units_context


async def _get_edge_data_with_docs(
    keywords,
    knowledge_graph_inst: BaseGraphStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
):
    """获取边数据，同时返回原始文档列表"""
    results = await relationships_vdb.query(keywords, top_k=query_param.top_k)

    if not len(results):
        return "", "", "", []

    edge_datas = await asyncio.gather(
        *[knowledge_graph_inst.get_edge(r["src_id"], r["tgt_id"]) for r in results]
    )

    if not all([n is not None for n in edge_datas]):
        logger.warning("Some edges are missing, maybe the storage is damaged")
    edge_degree = await asyncio.gather(
        *[knowledge_graph_inst.edge_degree(r["src_id"], r["tgt_id"]) for r in results]
    )
    edge_datas = [
        {"src_id": k["src_id"], "tgt_id": k["tgt_id"], "rank": d, **v}
        for k, v, d in zip(results, edge_datas, edge_degree)
        if v is not None
    ]
    edge_datas = sorted(
        edge_datas, key=lambda x: (x["rank"], x["weight"]), reverse=True
    )
    edge_datas = truncate_list_by_token_size(
        edge_datas,
        key=lambda x: x["description"],
        max_token_size=query_param.max_token_for_global_context,
    )

    use_entities = await _find_most_related_entities_from_relationships(
        edge_datas, query_param, knowledge_graph_inst
    )
    use_text_units = await _find_related_text_unit_from_relationships(
        edge_datas, query_param, text_chunks_db, knowledge_graph_inst
    )
    logger.info(
        f"Global query uses {len(use_entities)} entites, {len(edge_datas)} relations, {len(use_text_units)} text units"
    )

    relations_section_list = [
        ["id", "source", "target", "description", "keywords", "weight", "rank"]
    ]
    for i, e in enumerate(edge_datas):
        relations_section_list.append(
            [
                i,
                e["src_id"],
                e["tgt_id"],
                e["description"],
                e["keywords"],
                e["weight"],
                e["rank"],
            ]
        )
    relations_context = list_of_list_to_csv(relations_section_list)

    entites_section_list = [["id", "entity", "type", "description", "rank"]]
    for i, n in enumerate(use_entities):
        entites_section_list.append(
            [
                i,
                n["entity_name"],
                n.get("entity_type", "UNKNOWN"),
                n.get("description", "UNKNOWN"),
                n["rank"],
            ]
        )
    entities_context = list_of_list_to_csv(entites_section_list)

    text_units_section_list = [["id", "content"]]
    for i, t in enumerate(use_text_units):
        text_units_section_list.append([i, t["content"]])
    text_units_context = list_of_list_to_csv(text_units_section_list)
    
    # 返回原始文档列表
    documents = use_text_units
    
    return entities_context, relations_context, text_units_context, documents


async def _find_most_related_entities_from_relationships(
    edge_datas: list[dict],
    query_param: QueryParam,
    knowledge_graph_inst: BaseGraphStorage,
):
    entity_names = []
    seen = set()

    for e in edge_datas:
        if e["src_id"] not in seen:
            entity_names.append(e["src_id"])
            seen.add(e["src_id"])
        if e["tgt_id"] not in seen:
            entity_names.append(e["tgt_id"])
            seen.add(e["tgt_id"])

    node_datas = await asyncio.gather(
        *[knowledge_graph_inst.get_node(entity_name) for entity_name in entity_names]
    )

    node_degrees = await asyncio.gather(
        *[knowledge_graph_inst.node_degree(entity_name) for entity_name in entity_names]
    )
    node_datas = [
        {**n, "entity_name": k, "rank": d}
        for k, n, d in zip(entity_names, node_datas, node_degrees)
    ]

    node_datas = truncate_list_by_token_size(
        node_datas,
        key=lambda x: x["description"],
        max_token_size=query_param.max_token_for_local_context,
    )

    return node_datas


async def _find_related_text_unit_from_relationships(
    edge_datas: list[dict],
    query_param: QueryParam,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    knowledge_graph_inst: BaseGraphStorage,
):
    text_units = [
        split_string_by_multi_markers(dp["source_id"], [GRAPH_FIELD_SEP])
        for dp in edge_datas
    ]
    all_text_units_lookup = {}

    for index, unit_list in enumerate(text_units):
        for c_id in unit_list:
            if c_id not in all_text_units_lookup:
                chunk_data = await text_chunks_db.get_by_id(c_id)

                if chunk_data is not None and "content" in chunk_data:
                    all_text_units_lookup[c_id] = {
                        "data": chunk_data,
                        "order": index,
                    }

    if not all_text_units_lookup:
        logger.warning("No valid text chunks found")
        return []

    all_text_units = [{"id": k, **v} for k, v in all_text_units_lookup.items()]
    all_text_units = sorted(all_text_units, key=lambda x: x["order"])


    valid_text_units = [
        t for t in all_text_units if t["data"] is not None and "content" in t["data"]
    ]

    if not valid_text_units:
        logger.warning("No valid text chunks after filtering")
        return []

    truncated_text_units = truncate_list_by_token_size(
        valid_text_units,
        key=lambda x: x["data"]["content"],
        max_token_size=query_param.max_token_for_text_unit,
    )

    all_text_units: list[TextChunkSchema] = [t["data"] for t in truncated_text_units]

    return all_text_units


def combine_contexts(entities, relationships, sources):

    hl_entities, ll_entities = entities[0], entities[1]
    hl_relationships, ll_relationships = relationships[0], relationships[1]
    hl_sources, ll_sources = sources[0], sources[1]

    combined_entities = process_combine_contexts(hl_entities, ll_entities)

    combined_relationships = process_combine_contexts(
        hl_relationships, ll_relationships
    )

    combined_sources = process_combine_contexts(hl_sources, ll_sources)

    return combined_entities, combined_relationships, combined_sources


import networkx as nx
from collections import defaultdict
async def find_paths_and_edges_with_stats(graph, target_nodes):

    result = defaultdict(lambda: {"paths": [], "edges": set()})
    path_stats = {"1-hop": 0, "2-hop": 0, "3-hop": 0}   
    one_hop_paths = []
    two_hop_paths = []
    three_hop_paths = []

    async def dfs(current, target, path, depth):

        if depth > 3: 
            return
        if current == target: 
            result[(path[0], target)]["paths"].append(list(path))
            for u, v in zip(path[:-1], path[1:]):
                result[(path[0], target)]["edges"].add(tuple(sorted((u, v))))
            if depth == 1:
                path_stats["1-hop"] += 1
                one_hop_paths.append(list(path))
            elif depth == 2:
                path_stats["2-hop"] += 1
                two_hop_paths.append(list(path))
            elif depth == 3:
                path_stats["3-hop"] += 1
                three_hop_paths.append(list(path))
            return
        neighbors = graph.neighbors(current) 
        for neighbor in neighbors:
            if neighbor not in path:  
                await dfs(neighbor, target, path + [neighbor], depth + 1)

    for node1 in target_nodes:
        for node2 in target_nodes:
            if node1 != node2:
                await dfs(node1, node2, [node1], 0)

    for key in result:
        result[key]["edges"] = list(result[key]["edges"])

    return dict(result), path_stats , one_hop_paths, two_hop_paths, three_hop_paths
def bfs_weighted_paths(G, path, source, target, threshold, alpha):
    results = [] 
    edge_weights = defaultdict(float)  
    node = source
    follow_dict = {}

    for p in path:
        for i in range(len(p) - 1):  
            current = p[i]
            next_num = p[i + 1]

            if current in follow_dict:
                follow_dict[current].add(next_num)
            else:
                follow_dict[current] = {next_num}

    for neighbor in follow_dict[node]:
        edge_weights[(node, neighbor)] += 1/len(follow_dict[node])

        if neighbor == target:
            results.append(([node, neighbor]))
            continue
        
        if edge_weights[(node, neighbor)] > threshold:

            for second_neighbor in follow_dict[neighbor]:
                weight = edge_weights[(node, neighbor)] * alpha / len(follow_dict[neighbor])
                edge_weights[(neighbor, second_neighbor)] += weight

                if second_neighbor == target:
                    results.append(([node, neighbor, second_neighbor]))
                    continue

                if edge_weights[(neighbor, second_neighbor)] > threshold:    

                    for third_neighbor in follow_dict[second_neighbor]:
                        weight = edge_weights[(neighbor, second_neighbor)] * alpha / len(follow_dict[second_neighbor]) 
                        edge_weights[(second_neighbor, third_neighbor)] += weight

                        if third_neighbor == target :
                            results.append(([node, neighbor, second_neighbor, third_neighbor]))
                            continue
    path_weights = []
    for p in path:
        path_weight = 0
        for i in range(len(p) - 1):
            edge = (p[i], p[i + 1])
            path_weight += edge_weights.get(edge, 0)  
        path_weights.append(path_weight/(len(p)-1))

    combined = [(p, w) for p, w in zip(path, path_weights)]

    return combined
async def _find_most_related_edges_from_entities3(
    node_datas: list[dict],
    query_param: QueryParam,
    knowledge_graph_inst: BaseGraphStorage,
):  

    G = nx.Graph()
    edges = await knowledge_graph_inst.edges()
    nodes = await knowledge_graph_inst.nodes()

    for u, v in edges:
        G.add_edge(u, v) 
    G.add_nodes_from(nodes)
    source_nodes = [dp["entity_name"] for dp in node_datas]
    result, path_stats, one_hop_paths, two_hop_paths, three_hop_paths = await find_paths_and_edges_with_stats(G, source_nodes)


    threshold = 0.3
    alpha = 0.8 
    all_results = []
    
    for node1 in source_nodes: 
        for node2 in source_nodes: 
            if node1 != node2: 
                if (node1, node2) in result:
                    sub_G = nx.Graph()
                    paths = result[(node1,node2)]['paths']
                    edges = result[(node1,node2)]['edges']
                    sub_G.add_edges_from(edges)
                    results = bfs_weighted_paths(G, paths, node1, node2, threshold, alpha)
                    all_results+= results
    all_results = sorted(all_results, key=lambda x: x[1], reverse=True)
    seen = set()
    result_edge = []
    for edge, weight in all_results:
        sorted_edge = tuple(sorted(edge))
        if sorted_edge not in seen:
            seen.add(sorted_edge)  
            result_edge.append((edge, weight))  

    
    length_1 = int(len(one_hop_paths)/2)
    length_2 = int(len(two_hop_paths)/2) 
    length_3 = int(len(three_hop_paths)/2) 
    results = []
    if one_hop_paths!=[]:
        results = one_hop_paths[0:length_1]
    if two_hop_paths!=[]:
        results = results + two_hop_paths[0:length_2]
    if three_hop_paths!=[]:
        results  =results + three_hop_paths[0:length_3]

    length = len(results)
    total_edges = 15
    if length < total_edges:
        total_edges = length
    sort_result = []
    if result_edge:
        if len(result_edge)>total_edges:
            sort_result = result_edge[0:total_edges]
        else : 
            sort_result = result_edge
    final_result = []
    for edge, weight in sort_result:
        final_result.append(edge)

    relationship = []

    for path in final_result:
        if len(path) == 4:
            s_name,b1_name,b2_name,t_name = path[0],path[1],path[2],path[3]
            edge0 = await knowledge_graph_inst.get_edge(path[0], path[1]) or await knowledge_graph_inst.get_edge(path[1], path[0])
            edge1 = await knowledge_graph_inst.get_edge(path[1],path[2]) or await knowledge_graph_inst.get_edge(path[2], path[1])
            edge2 = await knowledge_graph_inst.get_edge(path[2],path[3]) or await knowledge_graph_inst.get_edge(path[3], path[2])
            if edge0==None or edge1==None or edge2==None:
                print(path,"边丢失")
                if edge0==None:
                    print("edge0丢失")
                if edge1==None:
                    print("edge1丢失")
                if edge2==None:
                    print("edge2丢失")
                continue
            e1 = "through edge ("+edge0["keywords"]+") to connect to "+s_name+" and "+b1_name+"."
            e2 = "through edge ("+edge1["keywords"]+") to connect to "+b1_name+" and "+b2_name+"."
            e3 = "through edge ("+edge2["keywords"]+") to connect to "+b2_name+" and "+t_name+"."
            s = await knowledge_graph_inst.get_node(s_name)
            s = "The entity "+s_name+" is a "+s["entity_type"]+" with the description("+s["description"]+")"
            b1 = await knowledge_graph_inst.get_node(b1_name)
            b1 = "The entity "+b1_name+" is a "+b1["entity_type"]+" with the description("+b1["description"]+")"
            b2 = await knowledge_graph_inst.get_node(b2_name)
            b2 = "The entity "+b2_name+" is a "+b2["entity_type"]+" with the description("+b2["description"]+")"
            t = await knowledge_graph_inst.get_node(t_name)
            t = "The entity "+t_name+" is a "+t["entity_type"]+" with the description("+t["description"]+")"
            relationship.append([s+e1+b1+"and"+b1+e2+b2+"and"+b2+e3+t])
        elif len(path) == 3:
            s_name,b_name,t_name = path[0],path[1],path[2]
            edge0 = await knowledge_graph_inst.get_edge(path[0], path[1]) or await knowledge_graph_inst.get_edge(path[1], path[0])
            edge1 = await knowledge_graph_inst.get_edge(path[1],path[2]) or await knowledge_graph_inst.get_edge(path[2], path[1])
            if edge0==None or edge1==None:
                print(path,"边丢失")
                continue
            e1 = "through edge("+edge0["keywords"]+") to connect to "+s_name+" and "+b_name+"."
            e2 = "through edge("+edge1["keywords"]+") to connect to "+b_name+" and "+t_name+"."
            s = await knowledge_graph_inst.get_node(s_name)
            s = "The entity "+s_name+" is a "+s["entity_type"]+" with the description("+s["description"]+")"
            b = await knowledge_graph_inst.get_node(b_name)
            b = "The entity "+b_name+" is a "+b["entity_type"]+" with the description("+b["description"]+")"
            t = await knowledge_graph_inst.get_node(t_name)
            t = "The entity "+t_name+" is a "+t["entity_type"]+" with the description("+t["description"]+")"
            relationship.append([s+e1+b+"and"+b+e2+t])
        elif len(path) == 2:
            s_name,t_name = path[0],path[1]
            edge0 = await knowledge_graph_inst.get_edge(path[0], path[1]) or await knowledge_graph_inst.get_edge(path[1], path[0])
            if edge0==None:
                print(path,"边丢失")
                continue
            e = "through edge("+edge0["keywords"]+") to connect to "+s_name+" and "+t_name+"."
            s = await knowledge_graph_inst.get_node(s_name)
            s = "The entity "+s_name+" is a "+s["entity_type"]+" with the description("+s["description"]+")"
            t = await knowledge_graph_inst.get_node(t_name)
            t = "The entity "+t_name+" is a "+t["entity_type"]+" with the description("+t["description"]+")"
            relationship.append([s+e+t])


    relationship = truncate_list_by_token_size(
          relationship, 
          key=lambda x: x[0],
          max_token_size=query_param.max_token_for_local_context,
    )

    reversed_relationship = relationship[::-1]
    return reversed_relationship