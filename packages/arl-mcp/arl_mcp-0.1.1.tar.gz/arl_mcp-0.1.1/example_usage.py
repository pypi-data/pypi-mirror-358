#!/usr/bin/env python3
"""
示例：如何使用 arl-mcp 包

这个脚本展示了如何通过 uvx 或直接安装使用 arl-mcp 包。
"""

import subprocess
import sys

def test_uvx_installation():
    """测试通过 uvx 运行包"""
    print("=== 测试 uvx 安装和运行 ===")
    
    # 方法1: 从本地 wheel 文件运行
    wheel_path = "./dist/arl_mcp-0.1.0-py3-none-any.whl"
    print(f"\n1. 从本地 wheel 文件运行:")
    print(f"   uvx --from {wheel_path} arl-mcp")
    
    # 方法2: 从当前目录运行
    print(f"\n2. 从当前目录运行:")
    print(f"   uvx --from . arl-mcp")
    
    # 方法3: 如果发布到 PyPI 后
    print(f"\n3. 从 PyPI 运行 (发布后):")
    print(f"   uvx arl-mcp")

def test_pip_installation():
    """测试通过 pip 安装"""
    print("\n=== 测试 pip 安装 ===")
    
    # 本地安装
    print(f"\n1. 本地开发安装:")
    print(f"   pip install -e .")
    
    # 从 wheel 文件安装
    print(f"\n2. 从 wheel 文件安装:")
    print(f"   pip install ./dist/arl_mcp-0.1.0-py3-none-any.whl")
    
    # 从 PyPI 安装 (发布后)
    print(f"\n3. 从 PyPI 安装 (发布后):")
    print(f"   pip install arl-mcp")

def show_package_info():
    """显示包信息"""
    print("\n=== 包信息 ===")
    print("包名: arl-mcp")
    print("版本: 0.1.0")
    print("命令行工具: arl-mcp")
    print("主要功能:")
    print("  - ARL 平台集成")
    print("  - 域名和 IP 提取")
    print("  - 子域名枚举")
    print("  - 站点发现")
    print("  - 文件泄露检测")

def show_usage_examples():
    """显示使用示例"""
    print("\n=== 使用示例 ===")
    
    print("\n1. 启动 MCP 服务器:")
    print("   arl-mcp")
    
    print("\n2. 在 Python 代码中使用:")
    print("   from arl_mcp import main")
    print("   main()")
    
    print("\n3. 通过 MCP 客户端调用工具函数:")
    print("   - extract_main_domain(packet)")
    print("   - add_scan_task(name, target, ...)")
    print("   - get_all_subdomains(domain)")
    print("   - query_ip_list(domain)")
    print("   - query_site_list(domain)")
    print("   - query_fileleak_list(domain)")

def main():
    """主函数"""
    print("ARL MCP 包使用指南")
    print("=" * 50)
    
    show_package_info()
    test_uvx_installation()
    test_pip_installation()
    show_usage_examples()
    
    print("\n=== 下一步 ===")
    print("1. 测试本地安装: pip install -e .")
    print("2. 测试 uvx 运行: uvx --from . arl-mcp")
    print("3. 发布到 PyPI: twine upload dist/*")
    print("4. 创建 GitHub 仓库并推送代码")
    
if __name__ == "__main__":
    main()