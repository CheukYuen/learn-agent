# Agent.py - 流式输出智能助手

## 📋 项目简介

这是一个支持流式输出的AI智能助手系统，包含天气查询和通用对话功能。基于Anthropic Claude API和MCP协议实现。

## 🚀 快速开始

### 环境配置
```bash
# 1. 安装依赖
pip install anthropic httpx python-dotenv requests

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的 ANTHROPIC_API_KEY_PLUS
```

### 运行方式
```bash
# 交互式模式
python agent.py

# 演示模式
python agent.py demo

# 测试流式输出
python test_stream.py
```

## 📊 架构文档

### 📁 本地架构图文件
- **`agent_architecture.md`** - 完整的架构文档，包含三个Mermaid图表：
  1. 🏗️ **整体系统架构图** - 展示所有组件和层次关系
  2. 🔄 **流式输出时序图** - 详细的流式处理流程
  3. 🏛️ **类结构图** - 代码结构和方法关系

### 🖼️ 查看架构图的方法

#### 方法1：在支持Mermaid的编辑器中查看
- **VS Code**: 安装 "Mermaid Preview" 扩展
- **Typora**: 直接支持Mermaid渲染
- **Obsidian**: 原生支持Mermaid图表

#### 方法2：在线Mermaid编辑器
1. 打开 [Mermaid Live Editor](https://mermaid.live/)
2. 复制 `agent_architecture.md` 中的Mermaid代码
3. 粘贴到编辑器中查看和导出

#### 方法3：GitHub查看
- 将文件推送到GitHub，GitHub原生支持Mermaid渲染

## 📁 文件结构

```
├── agent.py                # 主智能体文件
├── test_stream.py          # 流式输出测试
├── agent_architecture.md   # 📊 架构文档（包含图表）
├── README.md              # 本文件
└── .env                   # 环境变量配置
```

## 🎯 核心特性

- 🌤️ **天气查询**: 集成MCP天气工具
- 🔄 **流式输出**: 实时响应显示
- 🤖 **通用对话**: 支持各种AI任务
- 🛠️ **工具集成**: MCP协议工具调用
- 💻 **用户友好**: 命令切换和帮助系统

## 📖 使用示例

### 基本使用
```python
from agent import MCPWeatherAgent

# 创建智能体
agent = MCPWeatherAgent()

# 流式输出 - 实时显示响应
response = agent.chat("旧金山的天气如何？", stream=True)

# 非流式输出 - 一次性显示
response = agent.chat("纽约的天气如何？", stream=False)
```

### 交互式命令
- `旧金山的天气如何？` - 查询天气
- `/stream` - 切换流式/非流式模式
- `/help` - 显示帮助信息
- `quit` - 退出程序

## 🔧 技术栈

- **Python 3.8+**
- **Anthropic Claude API** - AI对话引擎
- **MCP协议** - 工具集成
- **流式输出** - 实时用户体验

---

**📊 详细架构说明请查看 `agent_architecture.md` 文件** 