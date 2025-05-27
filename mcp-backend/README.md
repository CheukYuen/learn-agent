# MCP Bridge Server

这是一个Node.js后端服务，用于智能体demo和MCP（Model Context Protocol）服务。

## 功能

- 提供RESTful API接口供智能体调用
- 桥接高德地图MCP服务
- 支持天气查询和地理编码功能

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 启动服务

开发模式（自动重启）：
```bash
npm run dev
```

生产模式：
```bash
npm start
```

服务将在 `http://localhost:3000` 启动。

## API接口

### 天气查询

**POST** `/api/mcp/weather`

请求体：
```json
{
  "city": "北京"
}
```

响应：
```json
{
  "success": true,
  "data": {
    "city": "北京",
    "adcode": "110000",
    "province": "北京",
    "reporttime": "2024-01-01 12:00:00",
    "casts": [
      {
        "date": "2024-01-01",
        "week": "一",
        "dayweather": "晴",
        "nightweather": "晴",
        "daytemp": "25",
        "nighttemp": "15",
        "daywind": "南风",
        "nightwind": "南风",
        "daypower": "≤3级",
        "nightpower": "≤3级"
      }
    ]
  }
}
```

### 地理编码

**POST** `/api/mcp/geo`

请求体：
```json
{
  "address": "北京市朝阳区"
}
```

响应：
```json
{
  "success": true,
  "data": {
    "formatted_address": "北京市朝阳区",
    "country": "中国",
    "province": "北京市",
    "city": "北京市",
    "adcode": "110000",
    "location": "116.397428,39.90923"
  }
}
```

### 健康检查

**GET** `/health`

响应：
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## 高德地图API集成

✅ **已集成高德地图API服务！**

当前版本已经集成了高德地图的REST API服务：

### 配置说明

1. **API Key**: 使用高德地图开放平台申请的API Key
2. **服务端点**: 
   - 地理编码: `https://restapi.amap.com/v3/geocode/geo`
   - 天气查询: `https://restapi.amap.com/v3/weather/weatherInfo`

### 工作原理

1. **主要调用**: 优先使用高德地图REST API
2. **备用机制**: 如果API调用失败，自动降级到模拟数据
3. **错误处理**: 完整的错误处理和日志记录

### API调用流程

```javascript
// 1. 地理编码获取城市adcode
const geoUrl = `https://restapi.amap.com/v3/geocode/geo?address=${encodeURIComponent(city)}&key=${apiKey}`;
const geoResponse = await fetch(geoUrl);
const geoData = await geoResponse.json();

// 2. 使用adcode查询天气
const weatherUrl = `https://restapi.amap.com/v3/weather/weatherInfo?city=${adcode}&key=${apiKey}&extensions=all`;
const weatherResponse = await fetch(weatherUrl);
const weatherData = await weatherResponse.json();
```

### 关于MCP协议

高德地图MCP服务使用SSE（Server-Sent Events）协议，需要特殊的客户端实现。为了简化集成，本项目直接使用高德地图的REST API，提供相同的功能。

## 部署

### Docker部署

创建 `Dockerfile`：

```dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

构建和运行：

```bash
docker build -t weather-mcp-bridge .
docker run -p 3000:3000 weather-mcp-bridge
```

### 云服务部署

可以部署到以下平台：
- 阿里云ECS
- 腾讯云CVM
- AWS EC2
- Vercel
- Railway

## 环境变量

可以通过环境变量配置：

```bash
PORT=3000                    # 服务端口
MCP_SERVER_URL=ws://...      # MCP服务器地址
AMAP_API_KEY=your_key_here   # 高德地图API密钥
```

## 注意事项

1. 确保防火墙开放3000端口
2. 生产环境建议使用HTTPS
3. 添加适当的错误处理和日志记录
4. 考虑添加API限流和认证机制 