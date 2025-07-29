# PagePathRAG

[![PyPI version](https://badge.fury.io/py/PagePathRAG.svg)](https://badge.fury.io/py/PagePathRAG)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PagePathRAG** 是一个强大的页面路径检索增强生成系统，专门用于将UI交互路径转化为知识图谱并进行智能查询的Python库。该系统结合了知识图谱、向量检索和大语言模型，为UI自动化测试、用户行为分析等领域提供智能化解决方案。

## 🚀 主要特性

- **智能路径解析**: 自动解析UI交互路径文本，提取关键实体和关系
- **知识图谱构建**: 将UI路径信息转化为结构化的知识图谱
- **混合检索系统**: 结合关键词检索和语义向量检索，提供精确的查询结果
- **自定义模型支持**: 支持自定义LLM和嵌入模型配置
- **灵活的提示词**: 可自定义实体提取和总结的提示词
- **批量处理**: 支持大规模UI路径数据的批量插入和处理

## 📦 安装

使用pip安装：

```bash
pip install PagePathRAG
```

或者从源码安装：

```bash
git clone https://github.com/your-username/PagePathRAG.git
cd PagePathRAG
pip install -e .
```

## 🔧 快速开始

### 基本使用

```python
from PagePathRAG import PagePathRAG, create_page_path_rag

# 创建PagePathRAG实例
rag = create_page_path_rag(
    api_key="your-openai-api-key",
    base_url="https://api.openai.com/v1",
    embedding_model_name="text-embedding-3-small",
    model_name="gpt-4o-mini",
    working_name="my_ui_project",
    working_dir="./data"
)

# 插入UI交互路径数据
ui_paths = [
    "点击页面底部频道按钮，进入频道tab页。在频道tab页中找到并点击一个新频道，进入该频道主页。",
    "点击设置页面，进入通知设置tab，激活推送通知按钮。",
    "在主页面滑动到顶部，点击搜索框，输入关键词进行搜索。"
]

rag.insert(ui_paths)

# 基于关键词查询
keywords = ["频道", "设置", "通知"]
result = rag.query_with_keywords(keywords, top_k=20)
print(result)
```

### 高级配置

```python
from PagePathRAG import PagePathRAG, PagePathRAGPrompt

# 自定义提示词
custom_prompt = PagePathRAGPrompt(
    entity_extraction="请从以下UI操作路径中提取实体...",
    entity_extraction_examples="示例1: ...\n示例2: ...",
    summarize_entity_descriptions="请总结以下实体的描述..."
)

# 创建实例并使用自定义提示词
rag = PagePathRAG(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    embedding_model_name="bge-large-zh",
    model_name="gpt-4",
    working_name="advanced_project",
    embedding_dim=1024,
    prompt=custom_prompt
)

# 批量插入预分片的文本块
chunks = [
    "点击页面底部频道按钮",
    "进入频道tab页", 
    "点击新频道进入主页"
]
rag.batch_insert(chunks, "ui_flows")

# 只获取上下文，不生成回答
context = rag.query_with_keywords(["频道"], return_context_only=True)
print(context)
```

## 📖 API 文档

### PagePathRAG 类

#### 初始化参数

- `api_key` (str): OpenAI API密钥
- `base_url` (str): API基础URL，默认为OpenAI API
- `embedding_model_name` (str): 嵌入模型名称
- `model_name` (str): 语言模型名称
- `working_name` (str): 工作空间名称，用于区分不同项目
- `working_dir` (str): 工作目录路径
- `embedding_dim` (int): 嵌入向量维度
- `prompt` (PagePathRAGPrompt): 自定义提示词实例

#### 主要方法

##### `insert(texts: List[str])`
插入UI路径文本列表到知识图谱中。

##### `query_with_keywords(keywords: List[str], top_k: int = 40, response_type: str = "Multiple Paragraphs", return_context_only: bool = False)`
基于关键词列表进行查询。

##### `batch_insert(chunk_list: List[str], source_name_prefix: str = "batch")`
批量插入预分片的文本块。

##### `delete_by_entity(entity_name: str)`
根据实体名称删除相关的实体和关系。

##### `clear_storage()`
清理所有存储数据。

##### `get_storage_info()`
获取存储状态信息。

### PagePathRAGPrompt 类

用于自定义提示词的数据类：

- `entity_extraction`: 实体提取提示词
- `entity_extraction_examples`: 实体提取示例
- `summarize_entity_descriptions`: 实体描述总结提示词

## 🏗️ 系统架构

PagePathRAG采用模块化设计：

```
PagePathRAG/
├── page_path_rag.py          # 主要API接口
├── PathRAG/                  # 核心功能模块
│   ├── PathRAG.py           # 主RAG系统
│   ├── base.py              # 基础数据结构
│   ├── llm.py               # LLM接口
│   ├── operate.py           # 操作工具
│   ├── prompt.py            # 提示词管理
│   ├── storage.py           # 存储管理
│   └── utils.py             # 工具函数
└── requirements.txt         # 依赖包列表
```

## 📋 依赖要求

主要依赖包：

- `openai`: OpenAI API客户端
- `transformers`: 深度学习模型
- `torch`: PyTorch深度学习框架
- `tiktoken`: 文本分词工具
- `networkx`: 图处理库
- `neo4j`: 图数据库驱动
- `pymilvus`: Milvus向量数据库客户端
- 其他支持库

完整依赖列表请查看 `requirements.txt` 文件。

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 🆘 支持

如果你遇到任何问题或有功能建议，请：

1. 查看 [文档](https://github.com/your-username/PagePathRAG#readme)
2. 搜索 [现有issues](https://github.com/your-username/PagePathRAG/issues)
3. 创建新的 [issue](https://github.com/your-username/PagePathRAG/issues/new)

## 🔄 更新日志

### v0.1.0 (2024-01-XX)
- 初始版本发布
- 基础UI路径解析功能
- 知识图谱构建和查询
- 支持自定义LLM和嵌入模型

---

**PagePathRAG** - 让UI交互路径智能化！🎯