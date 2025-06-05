"""
智能体实现 - 使用 Anthropic Claude 模型
简单的AI助手，支持对话和天气查询功能
"""

import os
from typing import Optional, List, Dict, Any, Generator
import anthropic
import httpx
from dotenv import load_dotenv
import time
import random
import requests
import json
import sys

# 加载环境变量
load_dotenv()


class AIAgent:
    """简单的AI智能体类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化智能体
        
        Args:
            api_key: Anthropic API密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("未找到Anthropic API密钥。请在环境变量中设置ANTHROPIC_API_KEY或直接传入api_key参数。")
        
        # 初始化Anthropic客户端
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            http_client=httpx.Client(
                proxy="http://127.0.0.1:7890/"  # 设置代理
            )
        )
        self.model = "claude-sonnet-4-20250514"
    
    def _make_api_call_with_retry(self, messages, system_prompt, max_retries=3, stream=False):
        """带重试机制的API调用，支持流式输出"""
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=messages,
                    stream=stream
                )
                
                if stream:
                    return response
                else:
                    return response.content[0].text
                    
            except anthropic.InternalServerError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # 指数退避
                    print(f"服务器错误，{wait_time:.1f}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise e
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 1 + random.uniform(0, 1)
                    print(f"请求失败，{wait_time:.1f}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise e
    
    def ask(self, question: str, system_prompt: str = "你是一个有用的AI助手。") -> str:
        """
        向智能体提问
        
        Args:
            question: 用户问题
            system_prompt: 系统提示词，定义智能体的角色
            
        Returns:
            智能体的回答
        """
        try:
            messages = [{"role": "user", "content": question}]
            return self._make_api_call_with_retry(messages, system_prompt)
                
        except anthropic.APIConnectionError as e:
            return f"连接错误: 无法连接到API服务器。请检查网络连接。详细错误: {str(e)}"
        except anthropic.AuthenticationError as e:
            return f"认证错误: API密钥无效。请检查ANTHROPIC_API_KEY环境变量。详细错误: {str(e)}"
        except anthropic.RateLimitError as e:
            return f"速率限制错误: API调用过于频繁。请稍后重试。详细错误: {str(e)}"
        except Exception as e:
            return f"未知错误: {type(e).__name__}: {str(e)}"
    
    def chat(self, messages: list, system_prompt: str = "你是一个有用的AI助手。") -> str:
        """
        多轮对话
        
        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
            system_prompt: 系统提示词
            
        Returns:
            智能体的回答
        """
        try:
            return self._make_api_call_with_retry(messages, system_prompt)
                
        except anthropic.APIConnectionError as e:
            return f"连接错误: 无法连接到API服务器。请检查网络连接。详细错误: {str(e)}"
        except anthropic.AuthenticationError as e:
            return f"认证错误: API密钥无效。请检查ANTHROPIC_API_KEY环境变量。详细错误: {str(e)}"
        except anthropic.RateLimitError as e:
            return f"速率限制错误: API调用过于频繁。请稍后重试。详细错误: {str(e)}"
        except Exception as e:
            return f"未知错误: {type(e).__name__}: {str(e)}"

    def chat_stream(self, messages: list, system_prompt: str = "你是一个有用的AI助手。") -> Generator[str, None, None]:
        """
        多轮对话的流式输出版本
        
        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
            system_prompt: 系统提示词
            
        Returns:
            生成器，产生智能体的回答片段
        """
        try:
            response = self._make_api_call_with_retry(messages, system_prompt, stream=True)
            
            # 处理流式响应
            for chunk in response:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text
                
        except anthropic.APIConnectionError as e:
            yield f"连接错误: 无法连接到API服务器。请检查网络连接。详细错误: {str(e)}"
        except anthropic.AuthenticationError as e:
            yield f"认证错误: API密钥无效。请检查ANTHROPIC_API_KEY环境变量。详细错误: {str(e)}"
        except anthropic.RateLimitError as e:
            yield f"速率限制错误: API调用过于频繁。请稍后重试。详细错误: {str(e)}"
        except Exception as e:
            yield f"未知错误: {type(e).__name__}: {str(e)}"


class WeatherAgent(AIAgent):
    """带天气查询功能的智能体类"""
    
    def __init__(self, api_key: Optional[str] = None, mcp_server_url: Optional[str] = None):
        """
        初始化天气智能体
        
        Args:
            api_key: Anthropic API密钥
            mcp_server_url: MCP 服务器 URL（可选）
        """
        super().__init__(api_key)
        
        # MCP 服务器配置（可选）
        self.mcp_server_url = mcp_server_url or "http://localhost:3001"
        self.mcp_sse_url = f"{self.mcp_server_url}/sse"
        
        # 检查 MCP 服务器是否可用（可选）
        if mcp_server_url:
            self._check_mcp_server()
    
    def _check_mcp_server(self):
        """检查 MCP 服务器是否可用"""
        try:
            health_url = f"{self.mcp_server_url}/health"
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                server_info = response.json()
                print(f"✅ MCP 服务器连接成功: {server_info.get('server', 'unknown')}")
            else:
                print("⚠️ MCP 服务器响应异常")
        except Exception as e:
            print(f"⚠️ 无法连接到 MCP 服务器: {e}")
    
    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """直接调用 MCP 工具"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = requests.post(
                self.mcp_sse_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"]
                    if content and len(content) > 0 and "text" in content[0]:
                        text_data = content[0]["text"]
                        return json.loads(text_data)
                    else:
                        raise Exception(f"MCP 工具返回内容格式异常")
                else:
                    raise Exception(f"MCP 工具调用失败")
            else:
                raise Exception(f"HTTP 错误: {response.status_code}")
                
        except Exception as e:
            return {"error": str(e)}
    
    def query_weather(self, city: str) -> str:
        """
        专门的天气查询方法
        
        Args:
            city: 要查询天气的城市名称
            
        Returns:
            天气查询结果
        """
        try:
            # 调用 MCP 工具获取天气数据
            weather_result = self._call_mcp_tool("get_weather", {"city": city})
            
            if "error" in weather_result:
                return f"天气查询失败: {weather_result['error']}"
            
            # 格式化天气数据
            if "weather" in weather_result:
                city_name = weather_result.get("city", city)
                province = weather_result.get("province", "")
                report_time = weather_result.get("reporttime", "")
                
                weather_info = [
                    f"📍 **{city_name}** ({province})",
                    f"🕐 数据更新时间: {report_time}",
                    ""
                ]
                
                for i, day_weather in enumerate(weather_result["weather"]):
                    if i == 0:
                        weather_info.append("**今天天气:**")
                    else:
                        weather_info.append(f"**{day_weather.get('week', f'第{i+1}天')}:**")
                    
                    weather_info.extend([
                        f"🌤️ 白天: {day_weather.get('dayweather', '未知')} | 夜间: {day_weather.get('nightweather', '未知')}",
                        f"🌡️ 温度: {day_weather.get('daytemp', '?')}°C / {day_weather.get('nighttemp', '?')}°C",
                        f"💨 风力: {day_weather.get('daywind', '未知')} {day_weather.get('daypower', '')}",
                        ""
                    ])
                
                return "\n".join(weather_info)
            else:
                return f"{city} 的天气查询完成，但数据格式异常。"
            
        except Exception as e:
            return f"天气查询失败: {str(e)}"


def main():
    """示例用法"""
    try:
        # 创建智能体实例
        agent = AIAgent()
        
        print("=== AI智能体演示 ===")
        print("✨ 这是一个简单的AI助手")
        print("💡 你可以和我聊任何话题")
        print("\n输入 'quit' 退出程序\n")
        
        # 简单的对话循环
        conversation_history = []
        
        while True:
            user_input = input("你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            # 添加用户消息到对话历史
            conversation_history.append({"role": "user", "content": user_input})
            
            # 获取智能体回答（流式输出）
            print("智能体: ", end="", flush=True)
            full_response = ""
            for chunk in agent.chat_stream(conversation_history):
                print(chunk, end="", flush=True)
                full_response += chunk
            print("\n")
            
            # 添加智能体回答到对话历史
            conversation_history.append({"role": "assistant", "content": full_response})
            
    except Exception as e:
        print(f"程序出错: {e}")
        print("请检查API密钥是否正确设置")


def demo_weather_query():
    """天气查询演示"""
    try:
        agent = WeatherAgent(mcp_server_url="http://localhost:3001")
        
        print("=== 天气查询演示 ===\n")
        
        # 测试几个城市的天气
        cities = ["北京", "上海", "广州", "深圳"]
        
        for city in cities:
            print(f"🌤️  查询 {city} 天气:")
            result = agent.query_weather(city)
            print(f"{result}\n")
            print("-" * 50)
            
    except Exception as e:
        print(f"演示出错: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_weather_query()
    else:
        main() 