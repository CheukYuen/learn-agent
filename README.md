# 智能体学习与 MCP 天气服务项目

这是一个用于学习和演示如何搭建智能体以及实现 Model Context Protocol (MCP) 服务的 Python 和 Node.js 项目。项目核心是使用 Anthropic Claude 模型构建一个具备天气查询能力的智能体。

## 🌟 项目亮点

-   🤖 **Python 智能体 (`agent.py`)**:
    -   基于 Anthropic Claude 模型。
    -   支持单轮和多轮对话。
    -   能够理解用户意图，特别是天气相关的查询。
    -   通过 MCP 服务调用外部工具获取实时天气信息。
    -   包含专门的天气查询方法和对话式天气查询。
    -   提供备用机制，在 MCP 服务不可用时仍能进行基本对话。
-   🌐 **Node.js MCP 天气服务器 (`mcp-backend/`)**:
    -   实现了 MCP 规范，作为智能体的工具提供者。
    -   提供 `get_weather` (天气查询) 和 `get_location` (地理编码) 工具。
    -   通过 SSE (Server-Sent Events) 和 JSON-RPC 与智能体通信。
    -   调用高德地图 API 获取真实的地理和天气数据。
    -   易于配置和启动。
-   📚 **丰富的使用示例和测试脚本**:
    -   `examples.py`: 智能体基础功能演示。
    -   `test_mcp_weather.py`: 针对天气查询功能的完整测试套件。
-   🔧 **易于扩展和定制**: 模块化设计，方便添加更多工具和智能体能力。

## 🚀 快速开始

### 1. 环境要求

-   Python 3.8+
-   Node.js >= 16.0.0
-   npm (Node Package Manager)
-   Anthropic API Key
-   高德地图 API Key (用于 MCP 服务器)

### 2. 安装依赖

**Python 智能体依赖:**

```bash
pip install -r requirements.txt
```

**Node.js MCP 服务器依赖:**

```bash
cd mcp-backend
npm install
```

### 3. 配置 API 密钥

#### a. Anthropic API Key (Python 智能体)

1.  在项目根目录下，复制环境变量示例文件：
    ```bash
    cp env.example .env
    ```
2.  编辑 `.env` 文件，添加您的 Anthropic API 密钥：
    ```env
    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    ```

#### b. 高德地图 API Key (Node.js MCP 服务器)

1.  在 `mcp-backend` 目录下创建一个 `.env` 文件 (如果尚不存在)。
2.  编辑 `mcp-backend/.env` 文件，添加您的高德地图 API Key：
    ```env
    AMAP_API_KEY=your_amap_api_key_here
    ```
    **注意**: `AMAP_API_KEY` 对于 MCP 服务器的正常运行至关重要。

### 4. 启动 MCP 天气服务器

切换到 `mcp-backend` 目录并启动服务器：

```bash
cd mcp-backend
npm run mcp
```

服务器默认运行在 `http://localhost:3001`。您应该能看到服务器成功启动并列出可用工具的消息。

### 5. 运行 Python 智能体

确保 MCP 服务器正在运行后，在项目根目录运行智能体：

**交互式天气对话:**

```bash
python agent.py
```

**专门的天气查询演示:**

```bash
python agent.py demo
```

**运行天气功能测试套件:**

```bash
python test_mcp_weather.py
```

**查看基础智能体功能示例:**

```bash
python examples.py
```

## 📁 项目结构

```
crisis-agent/
├── agent.py                # 主要的天气智能体类 (WeatherAgent)
├── examples.py             # 基础智能体功能使用示例
├── test_mcp_weather.py     # 天气查询功能测试脚本
├── requirements.txt        # Python 项目依赖
├── env.example             # Python 智能体环境变量示例
├── README.md               # 本项目说明
├── MCP_WEATHER_GUIDE.md    # MCP 天气查询系统详细指南
└── mcp-backend/            # Node.js MCP 天气服务器
    ├── mcp-server.js       # MCP 服务器核心逻辑
    ├── server.js           # (可选) 旧的 API 服务器
    ├── package.json        # Node.js 项目依赖和脚本
    ├── .env.example        # Node.js MCP 服务器环境变量示例 (建议创建)
    └── README.md           # MCP 服务器详细说明
```

## ⚙️ Python 智能体 (`agent.py`) 使用指南

`WeatherAgent` 类封装了与 Claude 模型的交互，并集成了通过 MCP 服务器进行天气查询的功能。

### 主要功能

-   **`__init__(api_key, mcp_server_url)`**: 初始化智能体，连接到 Anthropic API 和 MCP 服务器。
-   **`ask(question, system_prompt)`**: 单轮提问。如果问题与天气相关，会尝试通过 MCP 服务器获取信息并融入回答。
-   **`chat(messages, system_prompt)`**: 多轮对话。同样具备天气查询的智能判断。
-   **`query_weather(city)`**: 直接调用 MCP 服务器的 `get_weather` 工具查询指定城市的天气，并格式化输出。
-   **`_is_weather_query(question)`**: 判断问题是否与天气相关。
-   **`_call_mcp_tool(tool_name, arguments)`**: (内部方法) 实际调用 MCP 服务器工具的逻辑。

### 示例代码

```python
from agent import WeatherAgent

# 创建天气智能体实例
agent = WeatherAgent()

# 场景1: 直接查询特定城市天气
beijing_weather = agent.query_weather("北京")
print(f"北京天气预报:\n{beijing_weather}\n")

# 场景2: 对话式询问天气
print("与智能体对话 (输入 'quit' 退出):")
conversation_history = []

user_input = "你好"
conversation_history.append({"role": "user", "content": user_input})
response = agent.chat(conversation_history)
print(f"智能体: {response}")
conversation_history.append({"role": "assistant", "content": response})

user_input = "深圳今天天气怎么样？"
conversation_history.append({"role": "user", "content": user_input})
response = agent.chat(conversation_history)
print(f"智能体: {response}")
conversation_history.append({"role": "assistant", "content": response})
```

## 🔧 自定义和扩展

### Python 智能体 (`agent.py`)

-   **模型参数**: 在 `WeatherAgent` 类中，您可以调整 `model` (Claude 模型版本), `max_tokens`, `temperature` 等参数。
-   **添加新工具**: 参考 `_call_mcp_tool` 和 `query_weather` 的实现，您可以让智能体调用 MCP 服务器上的其他工具 (例如 `get_location`) 或新的 MCP 服务。
-   **提示词工程**: 优化 `system_prompt` 和传递给 Claude 的天气数据格式，以获得更精确或更自然的回答。

### Node.js MCP 服务器 (`mcp-backend/`)

-   **添加新工具**: 在 `mcp-server.js` 中定义新的工具 schema (在 `TOOLS`数组中)，并实现相应的工具逻辑函数 (类似 `getWeather` 和 `getLocation`)。
-   **修改数据源**: 您可以修改工具实现，使其从不同的 API 或数据源获取信息。

## 📚 学习路径与参考

1.  **基础使用** - 运行 `examples.py` 和 `agent.py`，理解 Anthropic API 的基本调用。
2.  **提示词工程** - 学习编写有效的 `system_prompt` 来引导智能体的行为和角色。
3.  **对话管理** - 研究 `agent.py` 中的 `chat` 方法，理解如何维护多轮对话的上下文。
4.  **MCP 服务理解** - 阅读 `mcp-backend/README.md` 和 `MCP_WEATHER_GUIDE.md`，理解 MCP 服务器的工作原理和 `mcp-server.js` 的实现。
5.  **工具调用集成** - 分析 `WeatherAgent` 中 `_call_mcp_tool` 和 `query_weather` 如何与 MCP 服务交互以实现天气查询。
6.  **功能扩展** - 尝试根据“后续扩展方向”添加新功能，例如为 MCP 服务添加新工具，或让 Python 智能体能够使用这些新工具。
7.  **生产部署考虑** - 思考如何将此类系统部署到生产环境，包括错误处理、日志记录、配置管理和安全性。

### 参考资料

-   **`MCP_WEATHER_GUIDE.md`**: 本项目中关于 MCP 天气查询系统的详细设置和使用指南。
-   **`mcp-backend/README.md`**: MCP 服务器的详细技术文档。
-   [Anthropic 官方文档](https://docs.anthropic.com/)
-   [Model Context Protocol (MCP) 规范](https://modelcontextprotocol.io/specification/2025-03-26/)
-   [高德开放平台文档](https://lbs.amap.com/api/webservice/guide/api/weatherinfo)

## ⚠️ 注意事项

-   **API 密钥安全**: 确保您的 Anthropic 和高德地图 API 密钥安全，不要将它们提交到版本控制中。使用 `.env` 文件进行管理。
-   **API 成本与限流**: 注意 API 调用可能产生的费用以及服务商的频率限制。
-   **MCP 服务器依赖**: Python 智能体的天气查询功能依赖于 `mcp-backend` 服务的正确运行。

## 💡 后续扩展方向 (结合 MCP 和智能体)

-   [ ] **完善 MCP 连接器支持**: 当 Anthropic Python SDK 正式发布并稳定支持 MCP 连接器后，迁移到官方实现，简化 `_call_mcp_tool` 部分。
-   [ ] **更智能的城市/地址提取**: 改进 `_extract_city_from_query` 方法，或在 MCP 服务端增加一个专门的 NLP 工具进行意图识别和槽位填充。
-   [ ] **多语言支持**: 使智能体能够理解多种语言的天气查询请求，并让 MCP 服务能够处理或翻译这些请求。
-   [ ] **集成更多 MCP 工具**: 例如，在 MCP 服务中添加日历查询、新闻摘要、简单计算等工具，并让智能体学会使用它们。
-   [ ] **上下文感知的工具推荐**: 让智能体能根据对话历史和当前用户问题，更智能地选择合适的 MCP 工具。
-   [ ] **用户界面**: 为智能体提供一个简单的 Web 界面或集成到如 Discord、Slack 等聊天应用中。
-   [ ] **错误处理与日志**: 增强智能体和 MCP 服务器的错误处理（例如，MCP 工具调用失败时的优雅降级）及详细的日志记录能力。
-   [ ] **配置化工具**: 允许通过配置文件动态加载和配置 MCP 工具，而不是硬编码。
-   [ ] **异步工具调用**: 如果 MCP 工具执行时间较长，研究如何在智能体中处理异步工具调用和响应。
-   [ ] **记忆管理**: 为智能体添加长期记忆功能，可以记住用户的偏好设置（例如常用城市）。
-   [ ] **流式响应**: 实现智能体和 MCP 工具的流式响应，以提升用户体验。

## �� 许可证

MIT License 