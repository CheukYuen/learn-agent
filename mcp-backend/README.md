# 高德地图天气查询 MCP 服务器

基于 Model Context Protocol (MCP) 的高德地图天气查询服务，提供标准化的天气查询接口。

## 🏗️ 架构概述

本项目包含两个服务器实现：

### 1. MCP 协议服务器 (`mcp-server.js`)
- **端口**: 3001
- **协议**: MCP v2025-03-26
- **传输**: HTTP + SSE (Server-Sent Events)
- **用途**: 为大模型提供标准 MCP 协议接口

### 2. HTTP API 服务器 (`server.js`)
- **端口**: 3000  
- **协议**: REST API
- **传输**: HTTP
- **用途**: 为前端应用提供简化的 HTTP 接口

## 🚀 快速开始

### 环境配置

1. **安装依赖**
```bash
npm install
```

2. **配置 API Key**
```bash
# 创建 .env 文件
echo "AMAP_API_KEY=your_actual_api_key" > .env
```

3. **获取高德 API Key**
- 访问 [高德开放平台](https://lbs.amap.com/api/webservice/create-project-and-key)
- 注册并创建应用
- 获取 Web 服务 API Key

### 启动服务

```bash
# 启动 MCP 服务器 (端口 3001)
npm run mcp

# 启动 HTTP API 服务器 (端口 3000)  
npm start

# 开发模式启动
npm run mcp-dev  # MCP 服务器热重载
npm run dev      # HTTP API 服务器热重载
```

## 📡 API 接口

### HTTP API 服务器 (端口 3000)

#### 1. 天气查询 (POST)
```bash
curl -X POST http://localhost:3000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"city": "北京"}'
```

#### 2. 天气查询 (GET)
```bash
curl http://localhost:3000/api/weather/北京
```

#### 3. 健康检查
```bash
curl http://localhost:3000/health
```

#### 4. API 文档
```bash
curl http://localhost:3000/
```

### MCP 协议服务器 (端口 3001)

#### 1. SSE 连接建立
```bash
curl -N http://localhost:3001/mcp
```

#### 2. 工具列表查询
```bash
curl http://localhost:3001/tools
```

#### 3. 健康检查
```bash
curl http://localhost:3001/health
```

## 🛠️ MCP 工具定义

### maps_weather
**功能**: 天气查询  
**参数**: 
- `city` (string, 必需): 城市名称或 adcode

**输入示例**:
```json
{
  "name": "maps_weather",
  "arguments": {
    "city": "北京"
  }
}
```

**输出示例**:
```json
{
  "content": [{
    "type": "text", 
    "text": "{\"city\":\"北京市\",\"province\":\"北京\",\"reporttime\":\"2025-06-05 17:10:43\",\"forecasts\":[{\"date\":\"2025-06-05\",\"week\":\"四\",\"dayweather\":\"晴\",\"nightweather\":\"晴\",\"daytemp\":\"25\",\"nighttemp\":\"15\",\"daywind\":\"南风\",\"nightwind\":\"南风\",\"daypower\":\"≤3级\",\"nightpower\":\"≤3级\"}]}"
  }],
  "isError": false
}
```

## 🔧 技术栈

- **Node.js**: >= 16.0.0
- **Express**: Web 框架
- **@modelcontextprotocol/sdk**: MCP 协议实现
- **node-fetch**: HTTP 请求客户端
- **dotenv**: 环境变量管理

## 📦 依赖说明

### 核心依赖
- `@amap/amap-maps-mcp-server`: 高德地图官方 MCP 服务器
- `@modelcontextprotocol/sdk`: MCP 协议 SDK
- `express`: HTTP 服务器框架
- `cors`: 跨域资源共享
- `node-fetch`: HTTP 请求库
- `dotenv`: 环境变量加载

### 开发依赖
- `nodemon`: 开发时热重载

## 🏃‍♂️ 使用场景

### 1. 大模型集成 (MCP 服务器)
```python
# 示例：在 Claude Desktop 配置中使用
{
  "mcpServers": {
    "amap-weather": {
      "command": "node",
      "args": ["mcp-server.js"],
      "cwd": "/path/to/mcp-backend",
      "env": {
        "AMAP_API_KEY": "your_api_key"
      }
    }
  }
}
```

### 2. 前端应用集成 (HTTP API)
```javascript
// 前端 JavaScript 调用
const response = await fetch('http://localhost:3000/api/weather/北京');
const weatherData = await response.json();
console.log(weatherData.data);
```

### 3. 其他服务集成
```bash
# Shell 脚本调用
weather=$(curl -s http://localhost:3000/api/weather/上海)
echo $weather | jq '.data.weather[0].dayweather'
```

## 🔍 错误处理

### API Key 错误
- 确保 `.env` 文件中的 `AMAP_API_KEY` 正确配置
- 验证 API Key 是否有效且有足够的调用次数

### 服务不可用
- 服务器会自动使用备用数据响应
- 检查网络连接和高德地图服务状态

### 端口冲突
- MCP 服务器: 端口 3001
- HTTP API 服务器: 端口 3000
- 可在代码中修改端口配置

## 📊 监控和调试

### 日志输出
- 服务器启动时显示完整配置信息
- API 调用会记录请求和响应状态
- 错误会自动记录详细信息

### 健康检查
```bash
# 检查服务状态
curl http://localhost:3000/health
curl http://localhost:3001/health

# 检查连接数 (MCP)
curl http://localhost:3001/health | jq '.connections'
```

## 🎯 最佳实践

1. **生产环境部署**
   - 使用 PM2 或类似进程管理器
   - 配置反向代理 (Nginx)
   - 启用 HTTPS

2. **API Key 安全**
   - 不要将 API Key 提交到代码仓库
   - 使用环境变量或密钥管理服务
   - 定期轮换 API Key

3. **性能优化**
   - 实现请求缓存
   - 设置合理的超时时间
   - 监控 API 调用频率

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [高德地图开放平台](https://lbs.amap.com/) - 提供天气数据 API
- [Model Context Protocol](https://github.com/modelcontextprotocol) - MCP 协议规范
- [@amap/amap-maps-mcp-server](https://www.npmjs.com/package/@amap/amap-maps-mcp-server) - 官方 MCP 实现参考 