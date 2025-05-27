const express = require('express');
const cors = require('cors');
const fetch = globalThis.fetch || require('node-fetch');
require('dotenv').config();

const app = express();
const port = 3001; // 使用不同端口避免冲突

// 中间件
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

app.use(express.json());

// MCP 协议相关的工具定义
const TOOLS = [
  {
    name: "get_weather",
    description: "获取指定城市的天气预报信息",
    inputSchema: {
      type: "object",
      properties: {
        city: {
          type: "string",
          description: "要查询天气的城市名称，例如：北京、上海、广州"
        }
      },
      required: ["city"]
    }
  },
  {
    name: "get_location",
    description: "获取指定地址的地理编码信息",
    inputSchema: {
      type: "object",
      properties: {
        address: {
          type: "string",
          description: "要查询的地址，例如：北京市朝阳区"
        }
      },
      required: ["address"]
    }
  }
];

// 高德地图 API 配置
const AMAP_API_KEY = process.env.AMAP_API_KEY;

// 天气查询工具实现
async function getWeather(city) {
  try {
    console.log(`Getting weather for city: ${city}`);
    
    // 首先进行地理编码获取城市adcode
    const geoUrl = `https://restapi.amap.com/v3/geocode/geo?address=${encodeURIComponent(city)}&key=${AMAP_API_KEY}`;
    const geoResponse = await fetch(geoUrl);
    const geoData = await geoResponse.json();
    
    if (geoData.status !== '1' || !geoData.geocodes || geoData.geocodes.length === 0) {
      throw new Error('Failed to get city geocode');
    }
    
    const adcode = geoData.geocodes[0].adcode;
    
    // 查询天气信息
    const weatherUrl = `https://restapi.amap.com/v3/weather/weatherInfo?city=${adcode}&key=${AMAP_API_KEY}&extensions=all`;
    const weatherResponse = await fetch(weatherUrl);
    
    if (!weatherResponse.ok) {
      throw new Error(`Weather API request failed: ${weatherResponse.status}`);
    }

    const weatherData = await weatherResponse.json();
    
    if (weatherData.status === '1' && weatherData.forecasts && weatherData.forecasts.length > 0) {
      const forecast = weatherData.forecasts[0];
      return {
        city: forecast.city,
        province: forecast.province,
        reporttime: forecast.reporttime,
        weather: forecast.casts.map(cast => ({
          date: cast.date,
          week: cast.week,
          dayweather: cast.dayweather,
          nightweather: cast.nightweather,
          daytemp: cast.daytemp,
          nighttemp: cast.nighttemp,
          daywind: cast.daywind,
          nightwind: cast.nightwind,
          daypower: cast.daypower,
          nightpower: cast.nightpower
        }))
      };
    } else {
      throw new Error('No weather data found');
    }
  } catch (error) {
    console.error('Weather query error:', error);
    throw error;
  }
}

// 地理编码工具实现
async function getLocation(address) {
  try {
    console.log(`Getting location for address: ${address}`);
    
    const geoUrl = `https://restapi.amap.com/v3/geocode/geo?address=${encodeURIComponent(address)}&key=${AMAP_API_KEY}`;
    const response = await fetch(geoUrl);
    
    if (!response.ok) {
      throw new Error(`Geo API request failed: ${response.status}`);
    }

    const geoData = await response.json();
    
    if (geoData.status === '1' && geoData.geocodes && geoData.geocodes.length > 0) {
      const geocode = geoData.geocodes[0];
      return {
        formatted_address: geocode.formatted_address,
        country: geocode.country,
        province: geocode.province,
        city: geocode.city,
        district: geocode.district,
        adcode: geocode.adcode,
        location: geocode.location,
        level: geocode.level
      };
    } else {
      throw new Error('No location data found');
    }
  } catch (error) {
    console.error('Location query error:', error);
    throw error;
  }
}

// MCP 协议处理函数
function createMcpResponse(id, result) {
  return {
    jsonrpc: "2.0",
    id: id,
    result: result
  };
}

function createMcpError(id, error) {
  return {
    jsonrpc: "2.0",
    id: id,
    error: {
      code: -32000,
      message: error.message
    }
  };
}

// SSE 端点 - MCP 协议主要接口
app.get('/sse', (req, res) => {
  // 设置 SSE headers
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
  });

  console.log('SSE connection established');

  // 发送初始化信息
  const initData = {
    jsonrpc: "2.0",
    method: "initialize",
    params: {
      protocolVersion: "2025-03-26",
      capabilities: {
        tools: {}
      },
      serverInfo: {
        name: "weather-mcp-server",
        version: "1.0.0"
      }
    }
  };

  res.write(`data: ${JSON.stringify(initData)}\n\n`);

  // 保持连接活跃
  const keepAlive = setInterval(() => {
    res.write(`data: ${JSON.stringify({ type: "ping" })}\n\n`);
  }, 30000);

  // 处理连接关闭
  req.on('close', () => {
    console.log('SSE connection closed');
    clearInterval(keepAlive);
    res.end();
  });
});

// MCP 协议 JSON-RPC 端点
app.post('/sse', async (req, res) => {
  try {
    const { jsonrpc, id, method, params } = req.body;
    
    console.log(`MCP request: ${method}`, params);

    let result;

    switch (method) {
      case 'initialize':
        result = {
          protocolVersion: "2025-03-26",
          capabilities: {
            tools: {}
          },
          serverInfo: {
            name: "weather-mcp-server",
            version: "1.0.0"
          }
        };
        break;

      case 'tools/list':
        result = {
          tools: TOOLS
        };
        break;

      case 'tools/call':
        const { name, arguments: toolArgs } = params;
        
        if (name === 'get_weather') {
          const weatherData = await getWeather(toolArgs.city);
          result = {
            content: [
              {
                type: "text",
                text: JSON.stringify(weatherData, null, 2)
              }
            ]
          };
        } else if (name === 'get_location') {
          const locationData = await getLocation(toolArgs.address);
          result = {
            content: [
              {
                type: "text",
                text: JSON.stringify(locationData, null, 2)
              }
            ]
          };
        } else {
          throw new Error(`Unknown tool: ${name}`);
        }
        break;

      default:
        throw new Error(`Unknown method: ${method}`);
    }

    res.json(createMcpResponse(id, result));
  } catch (error) {
    console.error('MCP request error:', error);
    res.status(500).json(createMcpError(req.body.id, error));
  }
});

// 健康检查
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    server: 'weather-mcp-server',
    timestamp: new Date().toISOString(),
    tools: TOOLS.map(tool => tool.name)
  });
});

// 启动 MCP 服务器
app.listen(port, () => {
  console.log(`MCP Weather Server running at http://localhost:${port}`);
  console.log('Available endpoints:');
  console.log('  GET /sse - MCP SSE connection');
  console.log('  POST /sse - MCP JSON-RPC calls');
  console.log('  GET /health - Health check');
  console.log('\nMCP Server Info:');
  console.log('  Protocol Version: 2025-03-26');
  console.log('  Available Tools:', TOOLS.map(t => t.name).join(', '));
}); 