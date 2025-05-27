"""
智能体实现 - 支持 MCP 天气查询功能
使用 Anthropic Claude 模型和 MCP 连接器
"""

import os
from typing import Optional, List, Dict, Any
import anthropic
import httpx
from dotenv import load_dotenv
import time
import random
import requests
import json

# 加载环境变量
load_dotenv()


class WeatherAgent:
    """智能体类，支持 MCP 天气查询功能"""
    
    def __init__(self, api_key: Optional[str] = None, mcp_server_url: Optional[str] = None):
        """
        初始化智能体
        
        Args:
            api_key: Anthropic API密钥，如果不提供则从环境变量读取
            mcp_server_url: MCP 服务器 URL，默认为本地服务器
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
        self.model = "claude-sonnet-4-20250514"  # 使用支持 MCP 的模型
        
        # MCP 服务器配置
        self.mcp_server_url = mcp_server_url or "http://localhost:3001"
        self.mcp_sse_url = f"{self.mcp_server_url}/sse"
        
        # 检查 MCP 服务器是否可用
        self._check_mcp_server()
    
    def _check_mcp_server(self):
        """检查 MCP 服务器是否可用"""
        try:
            health_url = f"{self.mcp_server_url}/health"
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                server_info = response.json()
                print(f"✅ MCP 服务器连接成功: {server_info.get('server', 'unknown')}")
                print(f"   可用工具: {', '.join(server_info.get('tools', []))}")
            else:
                print("⚠️ MCP 服务器响应异常，将使用备用模式")
        except Exception as e:
            print(f"⚠️ 无法连接到 MCP 服务器: {e}")
            print("   请确保 MCP 服务器正在运行 (npm run mcp)")
    
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
                    # 解析 MCP 返回的结构
                    content = result["result"]["content"]
                    if content and len(content) > 0 and "text" in content[0]:
                        # 解析嵌套的 JSON 字符串
                        text_data = content[0]["text"]
                        return json.loads(text_data)
                    else:
                        raise Exception(f"MCP 工具返回内容格式异常: {result}")
                else:
                    raise Exception(f"MCP 工具调用失败: {result}")
            else:
                raise Exception(f"HTTP 错误: {response.status_code}")
                
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return {"error": f"JSON 解析错误: {str(e)}"}
        except Exception as e:
            print(f"MCP 工具调用错误: {e}")
            return {"error": str(e)}
    
    def _make_api_call_with_mcp_simulation(self, messages: List[Dict], system_prompt: str, max_retries: int = 3):
        """模拟 MCP 连接器功能，直接调用 MCP 工具并将结果包含在提示中"""
        
        # 检查是否需要天气查询
        user_content = messages[-1].get("content", "") if messages else ""
        
        if self._is_weather_query(user_content):
            # 尝试从用户输入中提取城市名称
            city = self._extract_city_from_query(user_content)
            
            if city:
                # 调用天气工具
                weather_result = self._call_mcp_tool("get_weather", {"city": city})
                
                # 将天气数据包含在系统提示中
                enhanced_system_prompt = f"""{system_prompt}

你刚刚通过 MCP 工具查询了 {city} 的天气信息，以下是查询结果：

{json.dumps(weather_result, ensure_ascii=False, indent=2)}

请基于这些数据为用户提供友好、详细的天气信息回答。如果数据中有错误，请告知用户。"""
            else:
                # 如果没有提取到城市，要求用户指定
                enhanced_system_prompt = f"""{system_prompt}

用户询问了天气信息但没有指定具体城市。请友好地询问用户想查询哪个城市的天气。"""
        else:
            enhanced_system_prompt = system_prompt
        
        # 使用普通 API 调用
        return self._make_api_call_with_retry(messages, enhanced_system_prompt, max_retries)
    
    def _extract_city_from_query(self, query: str) -> Optional[str]:
        """从查询中提取城市名称"""
        # 简单的城市名称提取逻辑
        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "重庆", "天津", "武汉", "西安", "苏州"]
        
        for city in cities:
            if city in query:
                return city
        
        # 更复杂的提取逻辑可以在这里添加
        return None
        
    def _make_api_call_with_retry(self, messages, system_prompt, max_retries=3):
        """带重试机制的API调用"""
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=messages
                )
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
        
    def ask(self, question: str, system_prompt: str = "你是一个有用的AI助手，可以查询天气信息。") -> str:
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
            
            # 判断是否是天气相关查询，如果是则使用 MCP 模拟功能
            if self._is_weather_query(question):
                weather_system_prompt = """你是一个专业的天气助手，能够使用 MCP 工具查询天气信息。

当用户询问天气时，你需要：
1. 根据提供的天气数据为用户展示详细的天气信息
2. 将查询结果以友好、详细的方式呈现给用户
3. 包含温度、天气状况、风力等关键信息

如果用户没有指定城市，请询问用户想查询哪个城市的天气。"""
                return self._make_api_call_with_mcp_simulation(messages, weather_system_prompt)
            else:
                return self._make_api_call_with_retry(messages, system_prompt)
                
        except anthropic.APIConnectionError as e:
            return f"连接错误: 无法连接到API服务器。请检查网络连接。详细错误: {str(e)}"
        except anthropic.AuthenticationError as e:
            return f"认证错误: API密钥无效。请检查ANTHROPIC_API_KEY环境变量。详细错误: {str(e)}"
        except anthropic.RateLimitError as e:
            return f"速率限制错误: API调用过于频繁。请稍后重试。详细错误: {str(e)}"
        except Exception as e:
            return f"未知错误: {type(e).__name__}: {str(e)}"
    
    def _is_weather_query(self, question: str) -> bool:
        """判断是否是天气相关查询"""
        weather_keywords = ['天气', '温度', '气温', '下雨', '晴天', '阴天', '多云', '雨', '雪', '风', 'weather']
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in weather_keywords)
    
    def query_weather(self, city: str) -> str:
        """
        专门的天气查询方法
        
        Args:
            city: 要查询天气的城市名称
            
        Returns:
            天气查询结果
        """
        try:
            # 直接调用 MCP 工具获取天气数据
            weather_result = self._call_mcp_tool("get_weather", {"city": city})
            
            if "error" in weather_result:
                return f"天气查询失败: {weather_result['error']}"
            
            # 格式化天气数据为用户友好的格式
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
                        f"💨 风力: {day_weather.get('daywind', '未知')} {day_weather.get('daypower', '')} | {day_weather.get('nightwind', '未知')} {day_weather.get('nightpower', '')}",
                        ""
                    ])
                
                return "\n".join(weather_info)
            else:
                return f"{city} 的天气查询完成，但数据格式异常。"
            
        except Exception as e:
            return f"天气查询失败: {str(e)}"
    
    def chat(self, messages: list, system_prompt: str = "你是一个有用的AI助手，可以查询天气信息。") -> str:
        """
        多轮对话
        
        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
            system_prompt: 系统提示词
            
        Returns:
            智能体的回答
        """
        try:
            # 检查最后一条用户消息是否涉及天气
            last_user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break
            
            if self._is_weather_query(last_user_message):
                weather_system_prompt = """你是一个专业的天气助手，能够使用 MCP 工具查询天气信息。

当用户询问天气时，你需要：
1. 根据提供的天气数据为用户展示详细的天气信息
2. 将查询结果以友好、详细的方式呈现给用户
3. 包含温度、天气状况、风力等关键信息

请根据对话历史来理解用户的具体需求。"""
                return self._make_api_call_with_mcp_simulation(messages, weather_system_prompt)
            else:
                return self._make_api_call_with_retry(messages, system_prompt)
                
        except anthropic.APIConnectionError as e:
            return f"连接错误: 无法连接到API服务器。请检查网络连接。详细错误: {str(e)}"
        except anthropic.AuthenticationError as e:
            return f"认证错误: API密钥无效。请检查ANTHROPIC_API_KEY环境变量。详细错误: {str(e)}"
        except anthropic.RateLimitError as e:
            return f"速率限制错误: API调用过于频繁。请稍后重试。详细错误: {str(e)}"
        except Exception as e:
            return f"未知错误: {type(e).__name__}: {str(e)}"


def main():
    """示例用法"""
    try:
        # 创建智能体实例
        agent = WeatherAgent()
        
        print("=== 天气智能体演示 ===")
        print("✨ 功能介绍:")
        print("   - 普通对话交流")
        print("   - 天气查询 (支持中国各大城市)")
        print("   - 地理位置查询")
        print("\n💡 示例命令:")
        print("   - 北京今天天气怎么样？")
        print("   - 查询上海的天气")
        print("   - 广州明天会下雨吗？")
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
            
            # 获取智能体回答
            print("智能体正在思考...")
            response = agent.chat(conversation_history)
            print(f"智能体: {response}\n")
            
            # 添加智能体回答到对话历史
            conversation_history.append({"role": "assistant", "content": response})
            
    except Exception as e:
        print(f"程序出错: {e}")
        print("请检查:")
        print("1. API密钥是否正确设置")
        print("2. MCP服务器是否启动 (cd mcp-backend && npm run mcp)")
        print("3. 网络连接是否正常")


def demo_weather_query():
    """天气查询演示"""
    try:
        agent = WeatherAgent()
        
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