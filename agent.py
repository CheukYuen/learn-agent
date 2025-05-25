"""
简单智能体实现
使用 Anthropic Claude 模型
"""

import os
from typing import Optional
import anthropic
import httpx
from dotenv import load_dotenv
import time
import random

# 加载环境变量
load_dotenv()


class SimpleAgent:
    """简单的智能体类，封装Anthropic API调用"""
    
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
        self.model = "claude-3-5-haiku-20241022"  # 使用稳定的模型版本
        
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


def main():
    """示例用法"""
    try:
        # 创建智能体实例
        agent = SimpleAgent()
        
        print("=== 简单智能体演示 ===")
        print("输入 'quit' 退出程序\n")
        
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
            response = agent.chat(conversation_history)
            print(f"智能体: {response}\n")
            
            # 添加智能体回答到对话历史
            conversation_history.append({"role": "assistant", "content": response})
            
    except Exception as e:
        print(f"程序出错: {e}")
        print("请检查你的API密钥是否正确设置。")


if __name__ == "__main__":
    main() 