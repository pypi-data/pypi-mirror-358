#!/usr/bin/env python3
"""
PagePathRAG 构建和上传脚本
用于构建Python包并上传到PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """运行shell命令"""
    print(f"\n{'='*50}")
    print(f"执行: {description or command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("输出:")
        print(result.stdout)
    
    if result.stderr:
        print("错误:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"命令执行失败，退出代码: {result.returncode}")
        sys.exit(1)
    
    return result

def clean_build_artifacts():
    """清理构建产物"""
    print("\n清理旧的构建产物...")
    
    dirs_to_clean = ['build', 'dist', 'PagePathRAG.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除: {dir_name}")
    
    # 清理__pycache__目录
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"已删除: {pycache_path}")
                dirs.remove(dir_name)

def check_required_files():
    """检查必需的文件是否存在"""
    print("\n检查必需的文件...")
    
    required_files = [
        'setup.py',
        'pyproject.toml', 
        'README.md',
        'LICENSE',
        'requirements.txt',
        'PagePathRAG/__init__.py',
        'PagePathRAG/page_path_rag.py'
    ]
    
    missing_files = []
    for file_name in required_files:
        if not os.path.exists(file_name):
            missing_files.append(file_name)
        else:
            print(f"✓ {file_name}")
    
    if missing_files:
        print(f"\n❌ 缺少以下必需文件: {', '.join(missing_files)}")
        sys.exit(1)
    
    print("\n✓ 所有必需文件都存在")

def install_build_tools():
    """安装构建工具"""
    print("\n安装/更新构建工具...")
    
    tools = ['build', 'twine', 'wheel']
    for tool in tools:
        run_command(f"pip install --upgrade {tool}", f"安装/更新 {tool}")

def build_package():
    """构建Python包"""
    print("\n构建Python包...")
    run_command("python -m build", "构建包")

def check_package():
    """检查包的完整性"""
    print("\n检查包的完整性...")
    run_command("python -m twine check dist/*", "检查包")

def upload_to_test_pypi():
    """上传到测试PyPI"""
    print("\n上传到测试PyPI...")
    print("请确保你已经在 https://test.pypi.org 注册账号")
    print("并且配置了API token")
    
    choice = input("\n是否要上传到测试PyPI? (y/N): ").strip().lower()
    if choice in ['y', 'yes']:
        run_command(
            "python -m twine upload --repository testpypi dist/*",
            "上传到测试PyPI"
        )
        print("\n✓ 已上传到测试PyPI")
        print("可以使用以下命令测试安装:")
        print("pip install --index-url https://test.pypi.org/simple/ PagePathRAG")
        print("然后使用:")
        print("from PagePathRAG import PagePathRAG, PagePathRAGPrompt")

def upload_to_pypi():
    """上传到正式PyPI"""
    print("\n上传到正式PyPI...")
    print("⚠️  警告: 这将发布包到正式的PyPI，操作不可逆!")
    print("请确保你已经在 https://pypi.org 注册账号")
    print("并且配置了API token")
    
    choice = input("\n确定要上传到正式PyPI吗? (y/N): ").strip().lower()
    if choice in ['y', 'yes']:
        run_command(
            "python -m twine upload dist/*",
            "上传到正式PyPI"
        )
        print("\n✓ 已上传到正式PyPI")
        print("现在可以使用以下命令安装:")
        print("pip install PagePathRAG")
        print("然后使用:")
        print("from PagePathRAG import PagePathRAG, PagePathRAGPrompt")

def main():
    """主函数"""
    print("PagePathRAG 包构建和上传工具")
    print("=" * 40)
    
    try:
        # 检查必需文件
        check_required_files()
        
        # 清理旧的构建产物
        clean_build_artifacts()
        
        # 安装构建工具
        install_build_tools()
        
        # 构建包
        build_package()
        
        # 检查包
        check_package()
        
        print("\n" + "=" * 50)
        print("构建完成! 接下来选择上传选项:")
        print("1. 上传到测试PyPI (推荐先测试)")
        print("2. 上传到正式PyPI")
        print("3. 只构建，不上传")
        print("=" * 50)
        
        choice = input("\n请选择 (1/2/3): ").strip()
        
        if choice == "1":
            upload_to_test_pypi()
        elif choice == "2":
            upload_to_pypi()
        elif choice == "3":
            print("\n✓ 只构建完成，未上传")
        else:
            print("无效选择，只完成构建")
        
        print("\n🎉 所有操作完成!")
        
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 