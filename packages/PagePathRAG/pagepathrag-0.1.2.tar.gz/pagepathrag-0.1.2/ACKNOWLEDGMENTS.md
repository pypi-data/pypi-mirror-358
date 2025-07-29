# 致谢 (Acknowledgments)

## 基于开源项目

本项目 **PagePathRAG** 基于以下优秀的开源项目进行开发：

### PathRAG
- **原始项目**: [BUPT-GAMMA/PathRAG](https://github.com/BUPT-GAMMA/PathRAG)
- **开发团队**: BUPT-GAMMA (北京邮电大学)
- **相关论文**: "PathRAG: Pruning Graph-based Retrieval Augmented Generation with Relational Paths"
- **发表期刊**: arXiv preprint arXiv:2502.14902 (2025)

### 作者团队
感谢以下研究人员的杰出贡献：
- Chen, Boyu
- Guo, Zirui  
- Yang, Zidan
- Chen, Yuluo
- Chen, Junze
- Liu, Zhenghao
- Shi, Chuan
- Yang, Cheng

## 项目关系说明

### 基础架构
PagePathRAG的核心架构和算法基于原始PathRAG项目：
- 图-based检索增强生成 (Graph-based RAG)
- 关系路径剪枝算法
- 知识图谱构建和查询机制

### 扩展和改进
在原始项目基础上，PagePathRAG进行了以下扩展：
- **UI路径特化**: 专门针对UI交互路径场景进行优化
- **API封装**: 提供更友好、易用的Python API接口
- **提示词优化**: 针对UI元素和操作进行了提示词定制
- **配置简化**: 简化了模型配置和初始化流程

### 使用许可
请在使用本项目时：
1. 遵守原始PathRAG项目的许可证要求
2. 如在学术研究中使用，请同时引用原始论文
3. 保持对原作者团队的致谢

## 论文引用

如果您在研究中使用了本项目，请引用原始PathRAG论文：

```bibtex
@article{chen2025pathrag,
  title={PathRAG: Pruning Graph-based Retrieval Augmented Generation with Relational Paths},
  author={Chen, Boyu and Guo, Zirui and Yang, Zidan and Chen, Yuluo and Chen, Junze and Liu, Zhenghao and Shi, Chuan and Yang, Cheng},
  journal={arXiv preprint arXiv:2502.14902},
  year={2025}
}
```

## 感谢

再次感谢BUPT-GAMMA团队开发了如此优秀的PathRAG系统，为检索增强生成领域做出了重要贡献。本项目正是站在巨人的肩膀上，致力于将这一优秀技术应用到UI交互路径分析的特定场景中。

---

*最后更新时间: 2024年* 