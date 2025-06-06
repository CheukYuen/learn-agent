import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

// 创建服务器的工厂函数
export function createWeatherServer(name: string) {
  return new McpServer({
    name,
    version: "1.0.0",
    capabilities: {
      resources: {},
      tools: {},
    },
  });
} 