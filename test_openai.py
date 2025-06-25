import os
import httpx
from openai import OpenAI, DefaultHttpxClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_openai_api():
    """
    测试 OpenAI API 连接和基本功能
    使用代理配置确保网络连接
    """
    try:
        # 获取 API 密钥，优先使用环境变量，否则使用硬编码的密钥（仅用于测试）
        api_key = os.getenv("OPENAI_API_KEY")
        
        # 创建 OpenAI 客户端，配置代理
        client = OpenAI(
            api_key=api_key,
            http_client=DefaultHttpxClient(
                proxy="http://127.0.0.1:7890/"  # 设置代理
            )
        )
        
        print("🔗 正在连接 OpenAI API...")
        
        # 测试基本的聊天完成功能
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=150,
            messages=[
                {"role": "user", "content": "write a haiku about ai"}
            ]
        )
        
        print("✅ API 连接成功！")
        print("🤖 AI 回复:")
        print(completion.choices[0].message.content)
        
        # 显示使用情况信息
        if hasattr(completion, 'usage'):
            print(f"\n📊 使用情况:")
            print(f"   输入 tokens: {completion.usage.prompt_tokens}")
            print(f"   输出 tokens: {completion.usage.completion_tokens}")
            print(f"   总 tokens: {completion.usage.total_tokens}")
            
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查代理是否正常运行 (http://127.0.0.1:7890/)")
        print("2. 确认 OPENAI_API_KEY 环境变量已设置")
        print("3. 验证 API 密钥是否有效")
        print("4. 检查网络连接")

def test_multiple_models():
    """
    测试多个模型以验证 API 功能
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        
        client = OpenAI(
            api_key=api_key,
            http_client=DefaultHttpxClient(
                proxy="http://127.0.0.1:7890/"
            )
        )
        
        models_to_test = ["gpt-4o-mini", "gpt-3.5-turbo"]
        
        for model in models_to_test:
            print(f"\n🧪 测试模型: {model}")
            try:
                completion = client.chat.completions.create(
                    model=model,
                    max_tokens=50,
                    messages=[
                        {"role": "user", "content": "Hello! Say hi in one sentence."}
                    ]
                )
                print(f"✅ {model} 工作正常")
                print(f"   回复: {completion.choices[0].message.content}")
            except Exception as e:
                print(f"❌ {model} 测试失败: {str(e)}")
                
    except Exception as e:
        print(f"❌ 多模型测试失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始测试 OpenAI API")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  警告: OPENAI_API_KEY 环境变量未设置，使用硬编码密钥进行测试")
        print("建议在 .env 文件中添加: OPENAI_API_KEY=your_api_key_here")
    else:
        print("✅ 使用环境变量中的 API 密钥")
    
    # 运行基本测试
    test_openai_api()
    
    # 运行多模型测试
    print("\n" + "=" * 50)
    test_multiple_models()
    
    print("\n🎉 测试完成！") 