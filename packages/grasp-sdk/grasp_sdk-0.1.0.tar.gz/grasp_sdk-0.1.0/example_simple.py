#!/usr/bin/env python3
"""
Grasp SDK Python 简单示例

这个示例展示了如何在没有 API key 的情况下测试 grasp_sdk 的基本功能。
注意：这个示例主要用于测试包的导入和基本结构，实际的浏览器功能需要有效的 API key。
"""

import asyncio
import os
from pathlib import Path

try:
    from grasp_sdk import GraspServer, launch_browser
    from grasp_sdk.models import IBrowserConfig, ISandboxConfig
    print("✅ grasp_sdk 导入成功")
except ImportError as e:
    print(f"❌ 导入 grasp_sdk 失败: {e}")
    exit(1)


async def test_basic_functionality():
    """测试基本功能（不需要实际启动浏览器）"""
    
    print("\n🧪 测试基本功能...")
    
    try:
        # 测试 GraspServer 实例化
        server = GraspServer()
        print("✅ GraspServer 实例创建成功")
        
        # 测试获取状态
        status = server.get_status()
        print(f"✅ 服务器状态: {status}")
        
        # 测试获取沙箱 ID
        sandbox_id = server.get_sandbox_id()
        print(f"✅ 沙箱 ID: {sandbox_id}")
        
        print("\n✅ 基本功能测试通过")
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        raise


async def test_with_mock_config():
    """使用模拟配置测试（不实际连接）"""
    
    print("\n🔧 测试配置功能...")
    
    try:
        # 创建模拟的浏览器配置
        browser_config: IBrowserConfig = {
            'cdpPort': 9222,
            'headless': True,
            'launchTimeout': 30000,
            'args': ['--disable-web-security'],
            'envs': {'TEST': 'true'}
        }
        print("✅ 浏览器配置创建成功")
        
        # 创建模拟的沙箱配置
        sandbox_config: ISandboxConfig = {
            'key': 'mock_api_key',
            'templateId': 'playwright-pnpm-template',
            'timeout': 300000,
            'debug': False
        }
        print("✅ 沙箱配置创建成功")
        
        print("\n✅ 配置功能测试通过")
        
    except Exception as e:
        print(f"❌ 配置功能测试失败: {e}")
        raise


def test_imports():
    """测试所有重要模块的导入"""
    
    print("\n📦 测试模块导入...")
    
    try:
        # 测试服务模块
        from grasp_sdk.services import BrowserService, SandboxService
        print("✅ 服务模块导入成功")
        
        # 测试工具模块
        from grasp_sdk.utils import get_config, get_logger
        print("✅ 工具模块导入成功")
        
        # 测试模型模块
        from grasp_sdk.models import SandboxStatus
        print("✅ 模型模块导入成功")
        
        print("\n✅ 所有模块导入测试通过")
        
    except ImportError as e:
        print(f"❌ 模块导入测试失败: {e}")
        raise


async def main():
    """主函数：运行所有测试"""
    
    print("🎯 Grasp SDK Python 简单功能测试")
    print("=" * 50)
    
    try:
        # 1. 测试导入
        test_imports()
        
        # 2. 测试基本功能
        await test_basic_functionality()
        
        # 3. 测试配置
        await test_with_mock_config()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！")
        print("\n💡 提示：")
        print("   - 要运行完整的浏览器自动化示例，请使用 example_usage.py")
        print("   - 确保设置了有效的 GRASP_KEY 环境变量")
        print("   - 安装 Playwright：pip install playwright && playwright install")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n🔍 故障排除：")
        print("   1. 确保 grasp-sdk 已正确安装")
        print("   2. 检查 Python 版本（需要 3.8+）")
        print("   3. 查看完整错误信息以获取更多详情")
        raise


if __name__ == '__main__':
    # 运行测试
    asyncio.run(main())