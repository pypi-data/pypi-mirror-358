# PagePathRAG

[![PyPI version](https://badge.fury.io/py/PagePathRAG.svg)](https://badge.fury.io/py/PagePathRAG)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PagePathRAG** 是一个基于 [PathRAG](https://github.com/BUPT-GAMMA/PathRAG) 的页面路径检索增强生成系统，专门用于将UI交互路径转化为知识图谱并进行智能查询的Python库。该系统结合了知识图谱、向量检索和大语言模型，为UI自动化测试、用户行为分析等领域提供智能化解决方案。

> **基于开源项目**: 本项目基于 BUPT-GAMMA 团队的 [PathRAG](https://github.com/BUPT-GAMMA/PathRAG) 进行开发和扩展，专门针对UI交互路径场景进行了优化。

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
git clone https://github.com/cnatom/PagePathRAG.git
cd PagePathRAG
pip install -e .
```

> **注意**: 本项目基于 [PathRAG](https://github.com/BUPT-GAMMA/PathRAG)，如需了解核心算法原理，请参考原始项目。

## 🔧 快速开始

### 基本使用

```python
from PagePathRAG import PagePathRAG

# 创建PagePathRAG实例
rag = PagePathRAG(
    api_key="your-openai-api-key",
    base_url="https://api.openai.com/v1",
    embedding_model_name="text-embedding-3-small",
    model_name="gpt-4o-mini",
    working_name="my_ui_project",
    working_dir="./data"
)

# 插入UI交互路径数据
texts = [
    "从A页面点击B按钮进入B页面",
    "在B页面选择C选项后跳转到C页面",
    "从C页面点击返回按钮回到B页面",
    "在B页面点击设置按钮进入设置页面",
    "在设置页面调整通知开关",
    "从设置页面点击保存按钮返回B页面"
]

rag.insert(texts)

# 基于关键词查询UI路径
keywords = ["A页面","C页面"]
result = rag.query_with_paths(keywords, top_k=20)
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

# 插入文本
texts = [
    "从A页面点击B按钮进入B页面",
    "在B页面选择C选项后跳转到C页面",
    "从C页面点击返回按钮回到B页面",
    "在B页面点击设置按钮进入设置页面",
    "在设置页面调整通知开关",
    "从设置页面点击保存按钮返回B页面"
]
rag.insert(texts)

# 只获取上下文，不生成回答
context = rag.query_with_paths(["A页面","B页面"], return_context_only=True)
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

PagePathRAG对外提供两个核心接口：

##### `insert(texts: List[str])`
插入文本到知识图谱中。

**参数：**
- `texts`: 文本列表，每个文本通常包含UI交互路径描述

##### `query_with_paths(keywords: List[str], top_k: int = 40, response_type: str = "Multiple Paragraphs", return_context_only: bool = False)`
基于关键词列表查询相关的UI路径。

**参数：**
- `keywords`: 关键词列表，用于检索相关的UI交互路径
- `top_k`: 返回top-k个最相关的结果，默认40
- `response_type`: 响应类型，默认"Multiple Paragraphs"
- `return_context_only`: 是否只返回上下文，不生成回答，默认False

**返回值：**
- 如果`return_context_only=True`，返回上下文字符串
- 否则返回包含完整查询结果的字典，包含context、documents、path_entities等字段

### PagePathRAGPrompt 类

用于自定义提示词的数据类：

- `entity_extraction`: 实体提取提示词
- `entity_extraction_examples`: 实体提取示例
- `summarize_entity_descriptions`: 实体描述总结提示词

## 🏗️ 系统架构

PagePathRAG采用模块化设计，基于原始PathRAG架构进行扩展：

```
PagePathRAG/
├── page_path_rag.py          # 主要API接口（PagePathRAG封装层）
├── PathRAG/                  # 核心功能模块（基于原始PathRAG）
│   ├── PathRAG.py           # 主RAG系统
│   ├── base.py              # 基础数据结构
│   ├── llm.py               # LLM接口
│   ├── operate.py           # 操作工具
│   ├── prompt.py            # 提示词管理
│   ├── storage.py           # 存储管理
│   └── utils.py             # 工具函数
└── requirements.txt         # 依赖包列表
```

### 与原始PathRAG的关系

- **核心模块**: `PathRAG/` 目录包含基于原始PathRAG的核心功能
- **封装层**: `page_path_rag.py` 提供更友好的API接口
- **UI优化**: 专门针对UI交互路径场景进行了提示词和参数优化

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

## 🙏 致谢

本项目基于以下开源项目进行开发：

- **[PathRAG](https://github.com/BUPT-GAMMA/PathRAG)** - BUPT-GAMMA团队开发的图-based检索增强生成系统
- 相关论文：Chen, Boyu et al. "PathRAG: Pruning Graph-based Retrieval Augmented Generation with Relational Paths." arXiv preprint arXiv:2502.14902 (2025).

感谢原作者团队的杰出工作！

## 📚 引用

如果您在研究中使用了本项目，请同时引用原始PathRAG论文：

```bibtex
@article{chen2025pathrag,
  title={PathRAG: Pruning Graph-based Retrieval Augmented Generation with Relational Paths},
  author={Chen, Boyu and Guo, Zirui and Yang, Zidan and Chen, Yuluo and Chen, Junze and Liu, Zhenghao and Shi, Chuan and Yang, Cheng},
  journal={arXiv preprint arXiv:2502.14902},
  year={2025}
}
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

> **注意**: 本项目基于PathRAG进行扩展开发，请在使用时遵守原始项目的许可证要求。

## 🆘 支持

如果你遇到任何问题或有功能建议，请：

1. 查看 [文档](https://github.com/cnatom/PagePathRAG#readme)
2. 搜索 [现有issues](https://github.com/cnatom/PagePathRAG/issues)
3. 创建新的 [issue](https://github.com/cnatom/PagePathRAG/issues/new)

## 🔄 更新日志

### v0.1.0 (2024-01-XX)
- 初始版本发布
- 基础UI路径解析功能
- 知识图谱构建和查询
- 支持自定义LLM和嵌入模型

---

**PagePathRAG** - 让UI交互路径智能化！🎯