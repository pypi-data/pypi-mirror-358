from setuptools import setup, find_packages
import os

# 读取README文件作为长描述
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements.txt文件获取依赖
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = []
        for line in fh:
            line = line.strip()
            # 跳过空行和注释行
            if line and not line.startswith("#"):
                requirements.append(line)
        return requirements

setup(
    name="PagePathRAG",
    version="0.1.0",
    author="PagePathRAG Team",
    author_email="cnatom@icloud.com",
    description="基于PathRAG的页面路径检索增强生成系统 - 专门用于将UI交互路径转化为知识图谱并进行智能查询的Python库",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/PagePathRAG",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/PagePathRAG/issues",
        "Documentation": "https://github.com/your-username/PagePathRAG#readme",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords="rag, ui, path, knowledge-graph, llm, embedding, retrieval, ai",
    zip_safe=False,
) 