import express from 'express';
import cors from 'cors';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";
import { config } from 'dotenv';

config();

const app = express();
const port = 3001;

// 中间件
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

app.use(express.json());

// 获取高德 API Key
function getApiKey() {
    const apiKey = process.env.AMAP_API_KEY || process.env.AMAP_MAPS_API_KEY;
    if (!apiKey) {
        console.error("AMAP_API_KEY or AMAP_MAPS_API_KEY environment variable is not set");
        process.exit(1);
    }
    return apiKey;
}

const AMAP_MAPS_API_KEY = getApiKey();

// 天气查询工具定义
const WEATHER_TOOL = {
    name: "maps_weather",
    description: "根据城市名称或者标准adcode查询指定城市的天气",
    inputSchema: {
      type: "object",
      properties: {
        city: {
          type: "string",
                description: "城市名称或者adcode"
        }
      },
      required: ["city"]
    }
};

const TOOLS = [WEATHER_TOOL];

// 天气查询处理函数
async function handleWeather(city) {
  try {
    console.log(`Getting weather for city: ${city}`);
    
        const url = new URL("https://restapi.amap.com/v3/weather/weatherInfo");
        url.searchParams.append("city", city);
        url.searchParams.append("key", AMAP_MAPS_API_KEY);
        url.searchParams.append("source", "ts_mcp");
        url.searchParams.append("extensions", "all");
        
        const response = await fetch(url.toString());
    
        if (!response.ok) {
            throw new Error(`Weather API request failed: ${response.status}`);
    }

        const data = await response.json();
    
        if (data.status !== "1") {
            return {
                content: [{
                    type: "text",
                    text: `Get weather failed: ${data.info || data.infocode}`
                }],
                isError: true
            };
        }
        
      return {
            content: [{
                type: "text",
                text: JSON.stringify({
                    city: data.forecasts[0].city,
                    province: data.forecasts[0].province,
                    reporttime: data.forecasts[0].reporttime,
                    forecasts: data.forecasts[0].casts
                }, null, 2)
            }],
            isError: false
        };
  } catch (error) {
    console.error('Weather query error:', error);
        return {
            content: [{
                type: "text",
                text: `Error: ${error.message}`
            }],
            isError: true
        };
    }
}

// MCP 服务器设置
const server = new Server({
    name: "amap-weather-mcp-server",
    version: "1.0.0",
}, {
    capabilities: {
        tools: {},
    },
});

// 工具列表处理器
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: TOOLS,
}));

// 工具调用处理器
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
        switch (request.params.name) {
            case "maps_weather": {
                const { city } = request.params.arguments;
                return await handleWeather(city);
            }
            default:
      return {
                    content: [{
                        type: "text",
                        text: `Unknown tool: ${request.params.name}`
                    }],
                    isError: true
                };
    }
  } catch (error) {
        console.error('Tool call error:', error);
  return {
            content: [{
                type: "text",
                text: `Error: ${error instanceof Error ? error.message : String(error)}`
            }],
            isError: true
        };
    }
});

// 存储活跃的 SSE 连接
const sseConnections = new Map();

// SSE 连接端点 - GET 请求建立 SSE 流
app.get('/mcp', async (req, res) => {
    try {
        console.log('New SSE connection request');

        // 创建 SSE 传输
        const transport = new SSEServerTransport('/mcp', res);
        
        // 连接 MCP 服务器
        await server.connect(transport);
        
        // 启动 SSE 连接
        await transport.start();

        // 存储连接
        sseConnections.set(transport.sessionId, transport);
        
        console.log(`SSE connection established with session: ${transport.sessionId}`);
        
        // 处理连接关闭
        transport.onclose = () => {
            console.log(`SSE connection closed: ${transport.sessionId}`);
            sseConnections.delete(transport.sessionId);
        };
        
        transport.onerror = (error) => {
            console.error(`SSE connection error: ${transport.sessionId}`, error);
            sseConnections.delete(transport.sessionId);
        };
        
    } catch (error) {
        console.error('Failed to establish SSE connection:', error);
        res.status(500).json({ error: error.message });
          }
});

// POST 消息处理端点
app.post('/mcp', async (req, res) => {
    try {
        const sessionId = req.headers['x-session-id'];
        
        if (!sessionId) {
            return res.status(400).json({ error: 'Missing session ID' });
        }
        
        const transport = sseConnections.get(sessionId);
        
        if (!transport) {
            return res.status(404).json({ error: 'Session not found' });
        }
        
        // 处理 POST 消息
        await transport.handlePostMessage(req, res);
        
  } catch (error) {
        console.error('Failed to handle POST message:', error);
        res.status(500).json({ error: error.message });
  }
});

// 健康检查
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
        server: 'amap-weather-mcp-server',
    timestamp: new Date().toISOString(),
        protocol: 'MCP v2025-03-26',
        transport: 'HTTP/SSE',
        tools: TOOLS.map(tool => tool.name),
        connections: sseConnections.size
    });
});

// 获取工具列表的 HTTP 接口（用于调试）
app.get('/tools', (req, res) => {
    res.json({
        tools: TOOLS
  });
});

// 启动服务器
app.listen(port, () => {
    console.log(`🚀 Amap Weather MCP Server running at http://localhost:${port}`);
    console.log('📡 Available endpoints:');
    console.log('  GET  /mcp - MCP SSE connection');
    console.log('  POST /mcp - MCP JSON-RPC messages');
    console.log('  GET  /health - Health check');
    console.log('  GET  /tools - Available tools');
    console.log('\n🔧 MCP Server Info:');
    console.log('  Protocol Version: MCP v2025-03-26');
    console.log('  Transport: HTTP with SSE');
  console.log('  Available Tools:', TOOLS.map(t => t.name).join(', '));
    console.log(`  API Key: ${AMAP_MAPS_API_KEY ? 'Configured ✅' : 'Missing ❌'}`);
}); 