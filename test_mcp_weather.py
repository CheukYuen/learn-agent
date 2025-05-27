"""
测试 MCP 天气查询功能
"""

import os
import sys
from agent import WeatherAgent

def test_mcp_connection():
    """测试 MCP 服务器连接"""
    print("=== 测试 MCP 服务器连接 ===")
    try:
        agent = WeatherAgent()
        print("✅ MCP 连接测试成功！")
        return True
    except Exception as e:
        print(f"❌ MCP 连接失败: {e}")
        return False

def test_weather_query():
    """测试天气查询功能"""
    print("\n=== 测试天气查询功能 ===")
    try:
        agent = WeatherAgent()
        
        # 测试城市列表
        test_cities = ["北京", "上海", "广州"]
        
        for city in test_cities:
            print(f"\n🌤️  测试查询 {city} 天气:")
            result = agent.query_weather(city)
            print(f"结果: {result[:200]}...")  # 只显示前200个字符
            
        return True
    except Exception as e:
        print(f"❌ 天气查询测试失败: {e}")
        return False

def test_conversational_weather():
    """测试对话式天气查询"""
    print("\n=== 测试对话式天气查询 ===")
    try:
        agent = WeatherAgent()
        
        # 测试对话
        conversations = [
            "你好",
            "北京今天天气怎么样？",
            "上海呢？",
            "谢谢"
        ]
        
        history = []
        for msg in conversations:
            print(f"\n用户: {msg}")
            history.append({"role": "user", "content": msg})
            
            response = agent.chat(history)
            print(f"智能体: {response[:150]}...")  # 只显示前150个字符
            
            history.append({"role": "assistant", "content": response})
            
        return True
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 开始测试 MCP 天气查询系统\n")
    
    # 检查环境变量
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ 缺少 ANTHROPIC_API_KEY 环境变量")
        print("请在 .env 文件中设置你的 API 密钥")
        return False
    
    tests = [
        test_mcp_connection,
        test_weather_query,
        test_conversational_weather
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    # 总结测试结果
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 所有测试通过！MCP 天气查询系统工作正常。")
    else:
        print("\n⚠️  部分测试失败，请检查:")
        print("1. MCP 服务器是否正在运行 (cd mcp-backend && npm run mcp)")
        print("2. API 密钥是否正确配置")
        print("3. 网络连接是否正常")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 