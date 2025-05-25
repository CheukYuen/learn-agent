#!/usr/bin/env python3
"""
连接测试脚本
用于诊断和解决Anthropic API连接问题
"""

import os
import requests
import httpx
from dotenv import load_dotenv
from agent import SimpleAgent

def test_network_connection():
    """测试基本网络连接"""
    print("1. 测试基本网络连接...")
    
    test_urls = [
        "https://www.google.com",
        "https://api.anthropic.com"
    ]
    
    for url in test_urls:
        try:
            proxies = {"http": "http://127.0.0.1:7890/", "https": "http://127.0.0.1:7890/"}
            response = requests.get(url, timeout=10, proxies=proxies)
            print(f"   ✅ {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url} - 错误: {str(e)}")

def test_api_key():
    """测试API密钥配置"""
    print("\n2. 测试API密钥配置...")
    
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("   ❌ 未找到ANTHROPIC_API_KEY环境变量")
        print("   💡 请在.env文件中设置: ANTHROPIC_API_KEY=your_api_key_here")
        return False
    elif api_key == "your_anthropic_api_key_here":
        print("   ❌ API密钥仍是默认值，请设置真实的API密钥")
        return False
    elif len(api_key) < 10:
        print("   ❌ API密钥长度过短，可能不正确")
        return False
    else:
        print(f"   ✅ 找到API密钥 (长度: {len(api_key)}字符)")
        return True

def test_agent_creation():
    """测试智能体创建"""
    print("\n3. 测试智能体创建...")
    
    try:
        # 创建智能体
        agent = SimpleAgent()
        print("   ✅ 创建智能体成功")
        
        return agent
    except Exception as e:
        print(f"   ❌ 创建智能体失败: {str(e)}")
        return None

def test_api_call(agent):
    """测试API调用"""
    print(f"\n4. 测试API调用...")
    
    if agent is None:
        print("   ❌ 智能体未创建，跳过测试")
        return
    
    try:
        response = agent.ask("你好，请简单回复一句话测试连接。")
        
        if "错误" in response:
            print(f"   ❌ API调用失败: {response}")
        else:
            print(f"   ✅ API调用成功: {response[:50]}...")
    except Exception as e:
        print(f"   ❌ API调用异常: {str(e)}")

def main():
    """主测试函数"""
    print("=== Anthropic API 连接诊断工具 ===\n")
    
    # 测试网络连接
    test_network_connection()
    
    # 测试API密钥
    if not test_api_key():
        print("\n❌ API密钥配置有问题，请先解决API密钥问题")
        return
    
    # 测试智能体创建
    agent = test_agent_creation()
    
    # 测试API调用
    test_api_call(agent)
    
    print("\n=== 诊断完成 ===")
    print("\n💡 解决方案建议:")
    print("1. 如果API调用失败，请检查API密钥是否正确")
    print("2. 如果网络连接失败，请检查防火墙设置")
    print("3. 确保使用的是有效的Anthropic API密钥")

if __name__ == "__main__":
    main() 