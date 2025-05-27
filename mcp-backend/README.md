# MCP Weather Server (Node.js)

这是一个 Node.js 后端服务，它实现了 Model Context Protocol (MCP) 规范，并提供了天气查询和地理编码功能。该服务作为 Anthropic Claude 智能体的工具提供者。

## ✨ 功能

-   **MCP 协议实现**: 完全遵循 [MCP 规范 (2025-03-26)](https://modelcontextprotocol.io/specification/2025-03-26/)。
-   **SSE (Server-Sent Events) 支持**: 通过 `/sse` 端点提供 MCP 连接。
-   **JSON-RPC 支持**: 通过 `/sse` 端点的 POST 请求处理 MCP JSON-RPC 调用。
-   **天气查询工具 (`get_weather`)**: 调用高德地图 API 获取指定城市的天气信息。
-   **地理编码工具 (`get_location`)**: 调用高德地图 API 获取指定地址的地理编码信息。
-   **健康检查**: `/health` 端点提供服务状态和可用工具信息。
-   **环境变量配置**: 支持通过 `.env` 文件配置高德地图 API Key。

## 🛠️ 系统要求

-   Node.js >= 16.0.0
-   npm (Node Package Manager)
-   高德地图 API Key (需要在高德开放平台申请)

## 🚀 快速开始

### 1. 克隆仓库 (如果尚未克隆)

```bash
git clone <repository_url>
cd <repository_directory>/mcp-backend
```

### 2. 配置环境变量

在 `mcp-backend` 目录下创建一个 `.env` 文件，并添加您的高德地图 API Key：

```env
AMAP_API_KEY=your_amap_api_key_here
```

**注意**: `AMAP_API_KEY` 是必需的，否则服务将无法正确调用高德地图 API。示例中使用的 Key 可能随时失效。

### 3. 安装依赖

```bash
npm install
```

### 4. 启动 MCP 服务器

您可以使用以下任一命令启动服务器：

-   **开发模式 (使用 nodemon 实现热重载):**
    ```bash
    npm run mcp-dev
    ```
    或者直接运行:
    ```bash
    nodemon mcp-server.js
    ```

-   **生产模式:**
    ```bash
    npm run mcp
    ```
    或者直接运行:
    ```bash
    node mcp-server.js
    ```

服务器默认在 `http://localhost:3001` 启动。启动成功后，您会看到类似以下的输出：

```
MCP Weather Server running at http://localhost:3001
Available endpoints:
  GET /sse - MCP SSE connection
  POST /sse - MCP JSON-RPC calls
  GET /health - Health check

MCP Server Info:
  Protocol Version: 2025-03-26
  Available Tools: get_weather, get_location
```

## ⚙️ API 端点

### 1. MCP SSE 连接

-   **GET** `/sse`
-   **描述**: 建立 MCP Server-Sent Events 连接。客户端 (如 Anthropic Messages API) 通过此端点与 MCP 服务器通信。
-   **响应**:
    -   初始连接时，服务器会发送 `initialize` 消息，包含协议版本和服务器信息。
    -   之后，服务器会定期发送 `ping` 消息以保持连接活跃。
    -   当客户端通过 POST `/sse` 发起工具调用时，结果会通过此 SSE 连接异步返回。

### 2. MCP JSON-RPC 调用

-   **POST** `/sse`
-   **描述**: 处理 MCP JSON-RPC 请求，主要用于工具调用。
-   **请求体 (示例 - `tools/call`):**
    ```json
    {
      "jsonrpc": "2.0",
      "id": "request_id_123",
      "method": "tools/call",
      "params": {
        "name": "get_weather",
        "arguments": {
          "city": "北京"
        }
      }
    }
    ```
-   **支持的方法**:
    -   `initialize`: 返回服务器初始化信息 (通常由客户端在 GET `/sse` 连接时获取)。
    -   `tools/list`: 返回服务器可用的工具列表及其描述和输入模式。
    -   `tools/call`: 调用指定的工具并返回结果。
-   **响应 (示例 - `tools/call` 成功):**
    ```json
    {
      "jsonrpc": "2.0",
      "id": "request_id_123",
      "result": {
        "content": [
          {
            "type": "text",
            "text": "{"city":"北京市","province":"北京","reporttime":"YYYY-MM-DD HH:MM:SS","weather":[...]}"
          }
        ]
      }
    }
    ```
-   **响应 (示例 - 错误):**
    ```json
    {
      "jsonrpc": "2.0",
      "id": "request_id_123",
      "error": {
        "code": -32000,
        "message": "Error message here"
      }
    }
    ```

### 3. 健康检查

-   **GET** `/health`
-   **描述**: 检查 MCP 服务器的运行状态和可用工具。
-   **响应:**
    ```json
    {
      "status": "ok",
      "server": "weather-mcp-server",
      "timestamp": "YYYY-MM-DDTHH:MM:SS.sssZ",
      "tools": ["get_weather", "get_location"]
    }
    ```

## 🔧 工具详情

### 1. `get_weather`

-   **描述**: 获取指定城市的天气预报信息。
-   **输入模式 (`inputSchema`):**
    ```json
    {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "要查询天气的城市名称，例如：北京、上海、广州"
        }
      },
      "required": ["city"]
    }
    ```
-   **输出 (嵌套在 `result.content[0].text` 中的 JSON 字符串):**
    ```json
    {
      "city": "北京市",
      "province": "北京",
      "reporttime": "2025-05-27 16:02:40", // 示例时间
      "weather": [
        {
          "date": "2025-05-27",
          "week": "2", // 星期二
          "dayweather": "多云",
          "nightweather": "多云",
          "daytemp": "32",
          "nighttemp": "18",
          "daywind": "西南",
          "nightwind": "西南",
          "daypower": "1-3",
          "nightpower": "1-3"
        },
        // ... 未来几天的天气预报 ...
      ]
    }
    ```

### 2. `get_location`

-   **描述**: 获取指定地址的地理编码信息 (经纬度等)。
-   **输入模式 (`inputSchema`):**
    ```json
    {
      "type": "object",
      "properties": {
        "address": {
          "type": "string",
          "description": "要查询的地址，例如：北京市朝阳区"
        }
      },
      "required": ["address"]
    }
    ```
-   **输出 (嵌套在 `result.content[0].text` 中的 JSON 字符串):**
    ```json
    {
      "formatted_address": "北京市朝阳区",
      "country": "中国",
      "province": "北京市",
      "city": "北京市",
      "district": "朝阳区",
      "adcode": "110105",
      "location": "116.407526,39.90403", // 经度,纬度
      "level": "区县"
    }
    ```

## 🧪 测试 MCP 服务器 (手动)

您可以使用 `curl` 或 Postman 等工具手动测试 MCP 服务器的端点。

**示例：列出工具**

```bash
curl -X POST http://localhost:3001/sse \
     -H "Content-Type: application/json" \
     -d '{
           "jsonrpc": "2.0",
           "id": "test-list-tools",
           "method": "tools/list",
           "params": {}
         }' | jq
```

**示例：调用 `get_weather` 工具**

```bash
curl -X POST http://localhost:3001/sse \
     -H "Content-Type: application/json" \
     -d '{
           "jsonrpc": "2.0",
           "id": "test-get-weather",
           "method": "tools/call",
           "params": {
             "name": "get_weather",
             "arguments": {"city": "上海"}
           }
         }' | jq
```

## 📄 脚本说明

-   `mcp-server.js`: MCP 服务器的主要实现文件。
-   `package.json`: 定义项目依赖和启动脚本。
    -   `scripts.mcp`: 启动 MCP 服务器 (生产模式)。
    -   `scripts.mcp-dev`: 启动 MCP 服务器 (开发模式，使用 nodemon)。
-   `server.js`: (可选) 旧的 API 服务器，如果不再需要可以考虑移除或重构。

## 🔗 相关链接

-   [Model Context Protocol (MCP) 规范](https://modelcontextprotocol.io/specification/2025-03-26/)
-   [Anthropic MCP 连接器文档](https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector)
-   [高德开放平台](https://lbs.amap.com/)

## 🤝 贡献

欢迎通过 Pull Request 或 Issue 对本项目进行贡献。

## 📄 许可证

MIT 