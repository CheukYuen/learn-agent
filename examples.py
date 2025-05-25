"""
智能体使用示例
展示不同的使用场景和提示词技巧
"""

from agent import SimpleAgent


def example_basic_qa():
    """示例1: 基本问答"""
    print("=== 示例1: 基本问答 ===")
    agent = SimpleAgent()
    
    questions = [
        "什么是人工智能？",
        "Python中的装饰器是什么？",
        "如何学习机器学习？"
    ]
    
    for question in questions:
        print(f"问题: {question}")
        answer = agent.ask(question)
        print(f"回答: {answer}\n")


def example_role_based():
    """示例2: 基于角色的智能体"""
    print("=== 示例2: 专业角色智能体 ===")
    agent = SimpleAgent()
    
    # Python导师角色
    python_tutor_prompt = """你是一位经验丰富的Python编程导师。你擅长：
- 用简单易懂的方式解释复杂概念
- 提供实用的代码示例
- 给出学习建议和最佳实践
请用友好、耐心的语气回答问题。"""
    
    question = "我是Python初学者，如何理解函数和方法的区别？"
    print(f"问题: {question}")
    answer = agent.ask(question, python_tutor_prompt)
    print(f"Python导师: {answer}\n")
    
    # 创意写作助手角色
    creative_writer_prompt = """你是一位富有创意的写作助手。你擅长：
- 创作引人入胜的故事
- 提供创意灵感
- 改进文本的表达方式
请用富有想象力和创造性的方式回答。"""
    
    question = "帮我写一个关于时间旅行的短故事开头"
    print(f"问题: {question}")
    answer = agent.ask(question, creative_writer_prompt)
    print(f"创意写作助手: {answer}\n")


def example_conversation():
    """示例3: 多轮对话"""
    print("=== 示例3: 多轮对话 ===")
    agent = SimpleAgent()
    
    system_prompt = "你是一个友好的AI助手，擅长帮助用户解决问题。"
    
    # 模拟多轮对话
    conversation = [
        {"role": "user", "content": "我想学习编程，但不知道从哪里开始"},
        {"role": "assistant", "content": "学习编程是一个很棒的选择！我建议从Python开始，因为它语法简单，应用广泛。你有什么特定的目标吗？比如想做网站开发、数据分析还是其他方向？"},
        {"role": "user", "content": "我对数据分析比较感兴趣"},
    ]
    
    print("对话历史:")
    for msg in conversation:
        role = "用户" if msg["role"] == "user" else "智能体"
        print(f"{role}: {msg['content']}")
    
    print("\n继续对话...")
    response = agent.chat(conversation, system_prompt)
    print(f"智能体: {response}\n")


def example_structured_response():
    """示例4: 结构化回答"""
    print("=== 示例4: 结构化回答 ===")
    agent = SimpleAgent()
    
    structured_prompt = """你是一个专业的学习顾问。当回答学习相关问题时，请按以下格式组织回答：
1. 概述
2. 具体步骤
3. 推荐资源
4. 学习建议
请保持回答简洁但全面。"""
    
    question = "如何系统地学习Python编程？"
    print(f"问题: {question}")
    answer = agent.ask(question, structured_prompt)
    print(f"学习顾问: {answer}\n")


def main():
    """运行所有示例"""
    try:
        print("智能体使用示例演示\n")
        
        example_basic_qa()
        example_role_based()
        example_conversation()
        example_structured_response()
        
        print("所有示例演示完成！")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        print("请确保已正确设置API密钥。")


if __name__ == "__main__":
    main() 