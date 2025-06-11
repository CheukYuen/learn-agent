"""
简化的智能体实现 - 使用 Anthropic MCP Connector
支持通过MCP协议调用天气服务工具
"""

import os
from typing import Optional, List, Dict, Any
import anthropic
import httpx
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()


class MCPWeatherAgent:
    """使用 MCP Connector 的天气智能体"""
    
    def __init__(self, api_key: Optional[str] = None, mcp_server_url: Optional[str] = None):
        """
        初始化智能体
        
        Args:
            api_key: Anthropic API密钥，如果不提供则从环境变量读取
            mcp_server_url: MCP 服务器 URL，默认为本地服务器
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY_PLUS")
        if not self.api_key:
            raise ValueError("未找到Anthropic API密钥。请在环境变量中设置ANTHROPIC_API_KEY或直接传入api_key参数。")
        
        # 初始化Anthropic客户端
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url="https://anthropic.claude-plus.top",  # 设置中转 API URL，移除末尾的 /v1 避免路径重复
        )
        
        # MCP 服务器配置
        self.mcp_server_url = mcp_server_url or "http://localhost:3001/mcp"
        
        # 检查 MCP 服务器是否可用
        self._check_mcp_server()
    
    def _check_mcp_server(self):
        """检查 MCP 服务器是否可用"""
        try:
            # 检查健康状态
            health_url = self.mcp_server_url.replace('/mcp', '/health')
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                server_info = response.json()
                print(f"✅ MCP 服务器连接成功: {server_info.get('server', 'unknown')}")
                print(f"📡 可用工具: {', '.join(server_info.get('tools', []))}")
                return True
            else:
                print("⚠️ MCP 服务器响应异常")
                return False
        except Exception as e:
            print(f"⚠️ 无法连接到 MCP 服务器: {e}")
            return False
    
    def chat(self, message: str, system_prompt: str = None, stream: bool = False) -> str:
        """
        与智能体对话，自动使用MCP工具
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词，可选
            stream: 是否使用流式输出
            
        Returns:
            智能体的回答
        """
        if stream:
            return self.chat_stream(message, system_prompt)
        
        try:
            # 默认系统提示词
            if system_prompt is None:
                system_prompt = """你是一个有用的AI助手，专门帮助用户查询天气信息。
你可以使用以下工具：
- get-forecast: 获取指定坐标的天气预报
- get-alerts: 获取指定州的天气警报

当用户询问天气信息时，请使用这些工具来提供准确的信息。
美国主要城市坐标参考：
- 旧金山: 37.7749, -122.4194
- 纽约: 40.7128, -74.0060
- 洛杉矶: 34.0522, -118.2437
- 芝加哥: 41.8781, -87.6298
- 迈阿密: 25.7617, -80.1918"""
            
            # 使用 MCP Connector 调用 API
            response = self.client.beta.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message}
                ],
                mcp_servers=[
                    {
                        "type": "url",
                        "url": self.mcp_server_url,
                        "name": "weather-server",
                        "tool_configuration": {
                            "enabled": True,
                            "allowed_tools": ["get-forecast", "get-alerts"]
                        }
                    }
                ],
                betas=["mcp-client-2025-04-04"]
            )
            
            # 处理响应内容
            full_response = ""
            for content_block in response.content:
                if content_block.type == "text":
                    full_response += content_block.text
                elif content_block.type == "mcp_tool_use":
                    # MCP 工具使用信息
                    tool_info = f"\n🛠️ 正在使用工具: {content_block.name}"
                    if hasattr(content_block, 'server_name'):
                        tool_info += f" (来自: {content_block.server_name})"
                    full_response += tool_info
                elif content_block.type == "mcp_tool_result":
                    # MCP 工具结果已经集成在最终响应中
                    pass
                    
            return full_response
                
        except anthropic.APIConnectionError as e:
            return f"❌ 连接错误: 无法连接到API服务器。请检查网络连接。\n详细错误: {str(e)}"
        except anthropic.AuthenticationError as e:
            return f"❌ 认证错误: API密钥无效。请检查ANTHROPIC_API_KEY环境变量。\n详细错误: {str(e)}"
        except anthropic.RateLimitError as e:
            return f"❌ 速率限制错误: API调用过于频繁。请稍后重试。\n详细错误: {str(e)}"
        except Exception as e:
            return f"❌ 未知错误: {type(e).__name__}: {str(e)}"
    
    def chat_stream(self, message: str, system_prompt: str = None):
        """
        与智能体流式对话，实时输出响应
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词，可选
            
        Yields:
            逐步输出的文本片段
        """
        try:
            # 默认系统提示词
            if system_prompt is None:
                system_prompt = """你是一个有用的AI助手，专门帮助用户查询天气信息。
你可以使用以下工具：
- get-forecast: 获取指定坐标的天气预报
- get-alerts: 获取指定州的天气警报

当用户询问天气信息时，请使用这些工具来提供准确的信息。
美国主要城市坐标参考：
- 旧金山: 37.7749, -122.4194
- 纽约: 40.7128, -74.0060
- 洛杉矶: 34.0522, -118.2437
- 芝加哥: 41.8781, -87.6298
- 迈阿密: 25.7617, -80.1918"""
            
            # 使用流式 API 调用
            with self.client.beta.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message}
                ],
                mcp_servers=[
                    {
                        "type": "url",
                        "url": self.mcp_server_url,
                        "name": "weather-server",
                        "tool_configuration": {
                            "enabled": True,
                            "allowed_tools": ["get-forecast", "get-alerts"]
                        }
                    }
                ],
                betas=["mcp-client-2025-04-04"]
            ) as stream:
                full_response = ""
                
                for event in stream:
                    # 处理不同类型的流式事件
                    if event.type == "content_block_start":
                        content_block = event.content_block
                        if content_block.type == "text":
                            # 文本内容块开始
                            pass
                        elif content_block.type == "mcp_tool_use":
                            # MCP工具使用开始
                            tool_info = f"\n🛠️ 正在使用工具: {content_block.name}"
                            if hasattr(content_block, 'server_name'):
                                tool_info += f" (来自: {content_block.server_name})"
                            print(tool_info, end="", flush=True)
                            full_response += tool_info
                    
                    elif event.type == "content_block_delta":
                        delta = event.delta
                        if delta.type == "text_delta":
                            # 文本增量更新
                            text_chunk = delta.text
                            print(text_chunk, end="", flush=True)
                            full_response += text_chunk
                        elif delta.type == "input_json_delta":
                            # 工具输入的JSON增量（通常不需要显示）
                            pass
                    
                    elif event.type == "content_block_stop":
                        # 内容块结束
                        pass
                    
                    elif event.type == "message_delta":
                        # 消息级别的更新
                        pass
                    
                    elif event.type == "message_stop":
                        # 消息结束
                        break
                
                return full_response
                
        except anthropic.APIConnectionError as e:
            error_msg = f"❌ 连接错误: 无法连接到API服务器。请检查网络连接。\n详细错误: {str(e)}"
            print(error_msg)
            return error_msg
        except anthropic.AuthenticationError as e:
            error_msg = f"❌ 认证错误: API密钥无效。请检查ANTHROPIC_API_KEY环境变量。\n详细错误: {str(e)}"
            print(error_msg)
            return error_msg
        except anthropic.RateLimitError as e:
            error_msg = f"❌ 速率限制错误: API调用过于频繁。请稍后重试。\n详细错误: {str(e)}"
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ 未知错误: {type(e).__name__}: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_weather_forecast(self, city_name: str, latitude: float, longitude: float) -> str:
        """
        获取指定城市的天气预报
        
        Args:
            city_name: 城市名称（用于显示）
            latitude: 纬度
            longitude: 经度
            
        Returns:
            天气预报结果
        """
        message = f"请获取 {city_name} (纬度: {latitude}, 经度: {longitude}) 的天气预报"
        return self.chat(message)
    
    def get_weather_alerts(self, state_code: str) -> str:
        """
        获取指定州的天气警报
        
        Args:
            state_code: 州代码（如: CA, NY）
            
        Returns:
            天气警报结果
        """
        message = f"请获取 {state_code} 州的天气警报信息"
        return self.chat(message)


class SimpleAgent:
    """简化的通用AI智能体"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化智能体"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY_PLUS")
        if not self.api_key:
            raise ValueError("未找到Anthropic API密钥。请在环境变量中设置ANTHROPIC_API_KEY")
        
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url="https://anthropic.claude-plus.top",  # 设置中转 API URL，移除末尾的 /v1 避免路径重复
        )
    
    def ask(self, question: str, system_prompt: str = "你是一个有用的AI助手。", stream: bool = False) -> str:
        """简单的问答功能"""
        if stream:
            return self.ask_stream(question, system_prompt)
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": question}]
            )
            return response.content[0].text
        except Exception as e:
            return f"❌ 错误: {str(e)}"
    
    def ask_stream(self, question: str, system_prompt: str = "你是一个有用的AI助手。") -> str:
        """流式问答功能"""
        try:
            with self.client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": question}]
            ) as stream:
                full_response = ""
                
                for event in stream:
                    if event.type == "content_block_delta":
                        delta = event.delta
                        if delta.type == "text_delta":
                            text_chunk = delta.text
                            print(text_chunk, end="", flush=True)
                            full_response += text_chunk
                    elif event.type == "message_stop":
                        break
                
                return full_response
                
        except Exception as e:
            error_msg = f"❌ 错误: {str(e)}"
            print(error_msg)
            return error_msg


def main():
    """交互式演示"""
    print("=== MCP 天气智能体演示 (支持流式输出) ===")
    print("✨ 这是一个使用 MCP Connector 的天气助手")
    print("💡 你可以询问美国城市的天气情况")
    print("🌍 支持的功能：天气预报、天气警报")
    print("\n示例问题：")
    print("- 旧金山的天气如何？")
    print("- 加州有什么天气警报吗？")
    print("- 纽约明天会下雨吗？")
    print("\n💻 命令：")
    print("- '/stream' - 切换流式输出模式")
    print("- '/help' - 显示帮助")
    print("- 'quit' - 退出程序\n")
    
    try:
        agent = MCPWeatherAgent()
        stream_mode = True  # 默认启用流式输出
        print(f"🔄 当前模式: {'流式输出' if stream_mode else '普通输出'}\n")
        
        while True:
            user_input = input("你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if user_input == '/stream':
                stream_mode = not stream_mode
                print(f"🔄 已切换到: {'流式输出' if stream_mode else '普通输出'} 模式\n")
                continue
            
            if user_input == '/help':
                print("💡 可用命令：")
                print("- '/stream' - 切换流式输出模式")
                print("- '/help' - 显示此帮助")
                print("- 'quit' - 退出程序")
                print("🌤️ 询问天气示例：旧金山的天气如何？\n")
                continue
            
            if not user_input:
                continue
            
            print("智能体: ", end="", flush=True)
            
            if stream_mode:
                # 使用流式输出
                response = agent.chat(user_input, stream=True)
            else:
                # 使用普通输出
                response = agent.chat(user_input, stream=False)
                print(response)
            
            print("\n")  # 添加换行分隔
            
    except Exception as e:
        print(f"❌ 程序出错: {e}")
        print("请检查API密钥和MCP服务器是否正确设置")


def demo_weather_queries():
    """天气查询演示"""
    print("=== 天气查询演示 (流式输出) ===\n")
    
    try:
        agent = MCPWeatherAgent()
        
        # 演示天气预报查询 - 流式输出
        print("🌤️ 演示1: 获取旧金山天气预报 (流式输出)")
        print("结果: ", end="", flush=True)
        result = agent.chat(f"请获取旧金山 (纬度: 37.7749, 经度: -122.4194) 的天气预报", stream=True)
        print("\n" + "-" * 60)
        
        # 演示天气警报查询 - 流式输出
        print("⚠️ 演示2: 获取加州天气警报 (流式输出)")
        print("结果: ", end="", flush=True)
        result = agent.chat("请获取 CA 州的天气警报信息", stream=True)
        print("\n" + "-" * 60)
        
        # 演示自然语言查询 - 流式输出
        print("💬 演示3: 自然语言查询 (流式输出)")
        print("结果: ", end="", flush=True)
        result = agent.chat("纽约今天的天气怎么样？需要注意什么吗？", stream=True)
        print("\n" + "-" * 60)
        
        # 演示对比：非流式输出
        print("📝 演示4: 对比非流式输出")
        result = agent.chat("芝加哥的天气如何？", stream=False)
        print(f"结果: {result}\n")
        
    except Exception as e:
        print(f"❌ 演示出错: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_weather_queries()
    else:
        main() 