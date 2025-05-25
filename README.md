# 智能体学习项目

这是一个用于学习如何搭建智能体的简单Python项目，使用Anthropic Claude模型。

## 功能特性

- 🤖 简洁的智能体封装
- 💬 支持单轮和多轮对话
- 🎭 自定义角色和提示词
- 📚 丰富的使用示例
- 🔧 易于扩展和定制

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

1. 复制环境变量示例文件：
```bash
cp env.example .env
```

2. 编辑 `.env` 文件，添加你的Anthropic API密钥：
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. 运行示例

#### 基本对话
```bash
python agent.py
```

#### 查看使用示例
```bash
python examples.py
```

## 项目结构

```
crisis-agent/
├── agent.py          # 主要的智能体类
├── examples.py       # 使用示例
├── requirements.txt  # 项目依赖
├── env.example      # 环境变量示例
└── README.md        # 项目说明
```

## 使用指南

### 基本用法

```python
from agent import SimpleAgent

# 创建智能体实例
agent = SimpleAgent()

# 单轮问答
response = agent.ask("什么是人工智能？")
print(response)

# 自定义角色
system_prompt = "你是一位Python编程专家"
response = agent.ask("如何学习Python？", system_prompt)
print(response)
```

### 多轮对话

```python
# 准备对话历史
conversation = [
    {"role": "user", "content": "我想学编程"},
    {"role": "assistant", "content": "很好！你想学什么语言？"},
    {"role": "user", "content": "Python"}
]

# 继续对话
response = agent.chat(conversation)
print(response)
```

## 自定义和扩展

### 修改模型参数

在 `agent.py` 中的 `SimpleAgent` 类里，你可以调整：

- `model`: 使用的Claude模型版本
- `max_tokens`: 最大回复长度
- `temperature`: 回复的创造性（0-1）

### 添加新功能

你可以在 `SimpleAgent` 类中添加新方法，例如：

- 文档总结
- 代码生成
- 翻译功能
- 情感分析

## 学习路径

1. **基础使用** - 运行基本示例，理解API调用
2. **提示词工程** - 学习编写有效的system prompt
3. **对话管理** - 实现多轮对话和上下文管理
4. **功能扩展** - 添加工具调用、文档处理等高级功能
5. **生产部署** - 添加错误处理、日志、配置管理等

## 注意事项

- 确保API密钥安全，不要提交到版本控制
- 注意API调用的成本和频率限制
- 根据需要调整模型参数以平衡性能和成本

## 后续扩展方向

- [ ] 添加工具调用功能（Tool Use）
- [ ] 集成向量数据库进行知识检索
- [ ] 添加记忆管理功能
- [ ] 实现流式响应
- [ ] 添加Web界面
- [ ] 支持文件上传和处理

## 许可证

MIT License 