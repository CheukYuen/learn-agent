#!/usr/bin/env python3
"""
测试 Anthropic MCP Connector 功能
"""

import os
import anthropic
import httpx
from dotenv import load_dotenv

load_dotenv()

def test_mcp_connector():
    """测试MCP Connector"""
    
    # 检查API密钥
    api_key = os.getenv("ANTHROPIC_API_KEY_PLUS")
    if not api_key:
        print("❌ 未找到ANTHROPIC_API_KEY_PLUS环境变量")
        return
    
    print("🔑 API密钥已找到")
    
    # 创建客户端
    try:
        # 首先尝试不使用代理
        print("🌐 尝试直接连接（无代理）...")
        client = anthropic.Anthropic(
            api_key=api_key,
            base_url="https://anthropic.claude-plus.top",  # 设置中转 API URL，移除末尾的 /v1 避免路径重复
        )
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("✅ 直接连接成功")
        
    except Exception as e:
        print(f"❌ 直接连接失败: {e}")
        print("🌐 尝试使用代理...")
        
        try:
            client = anthropic.Anthropic(
                api_key=api_key,
                base_url="https://anthropic.claude-plus.top",  # 设置中转 API URL，移除末尾的 /v1 避免路径重复
            )
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print("✅ 代理连接成功")
            
        except Exception as e2:
            print(f"❌ 代理连接也失败: {e2}")
            return
    
    print("📞 基本API调用已验证，继续测试MCP...")
    
    # 测试MCP Connector功能
    try:
        print("🔌 测试MCP Connector...")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {"role": "user", "content": "What tools do you have available?"}
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": "http://localhost:3001/mcp",
                    "name": "weather-server",
                    "tool_configuration": {
                        "enabled": True,
                        "allowed_tools": ["get-forecast", "get-alerts"]
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ MCP Connector调用成功！")
        print(f"   响应内容类型: {[block.type for block in response.content]}")
        
        # 打印详细响应
        for i, block in enumerate(response.content):
            print(f"   内容块 {i+1}: {block.type}")
            if hasattr(block, 'text'):
                print(f"      文本: {block.text[:100]}...")
            elif hasattr(block, 'name'):
                print(f"      工具名: {block.name}")
                
    except Exception as e:
        print(f"❌ MCP Connector调用失败: {e}")
        print(f"   错误类型: {type(e).__name__}")


def test_weather_query():
    """测试天气查询"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ 未找到ANTHROPIC_API_KEY环境变量")
        return
    
    client = anthropic.Anthropic(
        api_key=api_key,
        http_client=httpx.Client(
            proxy="http://127.0.0.1:7890/"
        )
    )
    
    try:
        print("🌤️ 测试天气查询...")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system="你是一个天气助手。请使用get-forecast工具来获取旧金山(37.7749, -122.4194)的天气预报。",
            messages=[
                {"role": "user", "content": "请告诉我旧金山的天气情况"}
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": "http://localhost:3001/mcp",
                    "name": "weather-server"
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ 天气查询成功！")
        
        for i, block in enumerate(response.content):
            print(f"响应块 {i+1} ({block.type}):")
            if hasattr(block, 'text'):
                print(f"  文本: {block.text}")
            elif hasattr(block, 'name'):
                print(f"  工具: {block.name}")
            print()
        
    except Exception as e:
        print(f"❌ 天气查询失败: {e}")


if __name__ == "__main__":
    import sys
    
    print("=== Anthropic MCP Connector 测试 ===\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "weather":
        test_weather_query()
    else:
        test_mcp_connector() 