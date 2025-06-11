#!/usr/bin/env python3
"""
流式输出测试脚本
用于测试 agent.py 中的流式输出功能
"""

from agent import MCPWeatherAgent, SimpleAgent

def test_mcp_stream():
    """测试MCP智能体的流式输出"""
    print("=== 测试MCP智能体流式输出 ===\n")
    
    try:
        agent = MCPWeatherAgent()
        
        print("🧪 测试1: 流式输出")
        print("问题: 旧金山今天的天气如何？")
        print("回答: ", end="", flush=True)
        response = agent.chat("旧金山今天的天气如何？", stream=True)
        print(f"\n✅ 完整响应长度: {len(response)} 字符\n")
        
        print("🧪 测试2: 对比非流式输出")
        print("问题: 纽约的天气怎样？")
        response = agent.chat("纽约的天气怎样？", stream=False)
        print(f"回答: {response}")
        print(f"✅ 完整响应长度: {len(response)} 字符\n")
        
    except Exception as e:
        print(f"❌ MCP测试失败: {e}")

def test_simple_agent_stream():
    """测试简单智能体的流式输出"""
    print("=== 测试简单智能体流式输出 ===\n")
    
    try:
        agent = SimpleAgent()
        
        print("🧪 测试3: 简单智能体流式输出")
        print("问题: 解释一下什么是人工智能？")
        print("回答: ", end="", flush=True)
        response = agent.ask("解释一下什么是人工智能？", stream=True)
        print(f"\n✅ 完整响应长度: {len(response)} 字符\n")
        
        print("🧪 测试4: 对比非流式输出")
        print("问题: 什么是机器学习？")
        response = agent.ask("什么是机器学习？", stream=False)
        print(f"回答: {response}")
        print(f"✅ 完整响应长度: {len(response)} 字符\n")
        
    except Exception as e:
        print(f"❌ 简单智能体测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始流式输出功能测试...\n")
    
    # 测试MCP智能体
    test_mcp_stream()
    
    print("-" * 80)
    
    # 测试简单智能体
    test_simple_agent_stream()
    
    print("🎉 测试完成！")

if __name__ == "__main__":
    main() 