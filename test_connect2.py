import anthropic
import httpx
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 方式一：直连模式（需要代理）
# client = anthropic.Anthropic(
#   # 从环境变量读取 API 密钥
#   api_key=os.getenv("ANTHROPIC_API_KEY"),
#   base_url="https://api.anthropic.com",  # 设置 base URL
#   http_client=httpx.Client(
#     proxy="http://127.0.0.1:7890/"  # 设置代理
#   )
# )

# 方式二：中转API模式（无需代理）
client = anthropic.Anthropic(
  # 从环境变量读取 API 密钥
  api_key=os.getenv("ANTHROPIC_API_KEY_PLUS"),
  base_url="https://anthropic.claude-plus.top",  # 设置中转 API URL，移除末尾的 /v1 避免路径重复
)

# 切换到单个消息请求，因为中转API可能不支持批量处理（batches）
message = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hey Claude, tell me a short fun fact about video games! 中文",
        }
    ],
)
print(message)


message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hey Claude sonnet 4, tell me a short fun fact about video games! 中文",
        }
    ],
)
print(message)

# message_batch = client.messages.batches.create(
#     requests=[
#         {
#             "custom_id": "first-prompt-in-my-batch",
#             "params": {
#                 "model": "claude-3-5-haiku-20241022",
#                 "max_tokens": 100,
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": "Hey Claude, tell me a short fun fact about video games!",
#                     }
#                 ],
#             },
#         },
#         {
#             "custom_id": "second-prompt-in-my-batch",
#             "params": {
#                 "model": "claude-sonnet-4-20250514",
#                 "max_tokens": 100,
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": "Hey Claude, tell me a short fun fact about bees!",
#                     }
#                 ],
#             },
#         },
#     ]
# )
# print(message_batch)