#!/usr/bin/env node

// 简单的HTTP MCP服务器测试脚本

const baseUrl = 'http://localhost:3001';

// 解析SSE格式的响应
function parseSSEResponse(sseText) {
  const lines = sseText.split('\n');
  const events = [];
  let currentEvent = {};
  
  for (const line of lines) {
    if (line.startsWith('event:')) {
      currentEvent.event = line.substring(6).trim();
    } else if (line.startsWith('data:')) {
      currentEvent.data = line.substring(5).trim();
      try {
        currentEvent.parsedData = JSON.parse(currentEvent.data);
      } catch (e) {
        // data不是JSON格式
      }
    } else if (line === '') {
      // 空行表示事件结束
      if (currentEvent.data) {
        events.push(currentEvent);
        currentEvent = {};
      }
    }
  }
  
  return events;
}

async function testHealthCheck() {
  console.log('🏥 Testing health check...');
  try {
    const response = await fetch(`${baseUrl}/health`);
    const data = await response.json();
    console.log('✅ Health check:', data);
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
  }
}

async function testMcpInitialize() {
  console.log('\n📡 Testing MCP initialize...');
  try {
    const response = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {},
          clientInfo: {
            name: 'test-client',
            version: '1.0.0'
          }
        }
      })
    });
    
    console.log('📝 Response status:', response.status);
    console.log('📝 Content-Type:', response.headers.get('content-type'));
    
    const responseText = await response.text();
    
    if (response.headers.get('content-type')?.includes('text/event-stream')) {
      const events = parseSSEResponse(responseText);
      if (events.length > 0 && events[0].parsedData) {
        console.log('✅ Initialize response:', JSON.stringify(events[0].parsedData, null, 2));
      } else {
        console.log('📝 SSE events:', events);
      }
    } else {
      try {
        const data = JSON.parse(responseText);
        console.log('✅ Initialize response:', JSON.stringify(data, null, 2));
      } catch (parseError) {
        console.log('❌ JSON parse error:', parseError.message);
        console.log('📝 Raw response:', responseText);
      }
    }
  } catch (error) {
    console.error('❌ Initialize failed:', error.message);
  }
}

async function testListTools() {
  console.log('\n🛠️  Testing list tools...');
  try {
    const response = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 2,
        method: 'tools/list'
      })
    });
    
    const responseText = await response.text();
    const events = parseSSEResponse(responseText);
    
    if (events.length > 0 && events[0].parsedData) {
      console.log('✅ Tools list:', JSON.stringify(events[0].parsedData, null, 2));
    } else {
      console.log('📝 SSE events:', events);
    }
  } catch (error) {
    console.error('❌ List tools failed:', error.message);
  }
}

async function testWeatherForecast() {
  console.log('\n🌤️  Testing weather forecast for San Francisco...');
  try {
    const response = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 3,
        method: 'tools/call',
        params: {
          name: 'get-forecast',
          arguments: {
            latitude: 37.7749,
            longitude: -122.4194
          }
        }
      })
    });
    
    const responseText = await response.text();
    const events = parseSSEResponse(responseText);
    
    if (events.length > 0 && events[0].parsedData) {
      const data = events[0].parsedData;
      if (data.result?.content?.[0]?.text) {
        console.log('✅ Weather forecast preview:', data.result.content[0].text.substring(0, 300) + '...');
      } else {
        console.log('✅ Weather forecast response:', JSON.stringify(data, null, 2));
      }
    } else {
      console.log('📝 SSE events:', events);
    }
  } catch (error) {
    console.error('❌ Weather forecast failed:', error.message);
  }
}

async function testWeatherAlerts() {
  console.log('\n⚠️  Testing weather alerts for CA...');
  try {
    const response = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 4,
        method: 'tools/call',
        params: {
          name: 'get-alerts',
          arguments: {
            state: 'CA'
          }
        }
      })
    });
    
    const responseText = await response.text();
    const events = parseSSEResponse(responseText);
    
    if (events.length > 0 && events[0].parsedData) {
      const data = events[0].parsedData;
      if (data.result?.content?.[0]?.text) {
        console.log('✅ Weather alerts preview:', data.result.content[0].text.substring(0, 300) + '...');
      } else {
        console.log('✅ Weather alerts response:', JSON.stringify(data, null, 2));
      }
    } else {
      console.log('📝 SSE events:', events);
    }
  } catch (error) {
    console.error('❌ Weather alerts failed:', error.message);
  }
}

async function testFullMcpFlow() {
  console.log('\n🔄 Testing full MCP initialization flow...');
  
  // Step 1: Initialize
  try {
    const initResponse = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 'init-1',
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {
            tools: {}
          },
          clientInfo: {
            name: 'test-client',
            version: '1.0.0'
          }
        }
      })
    });
    
    const initText = await initResponse.text();
    const initEvents = parseSSEResponse(initText);
    const initData = initEvents[0]?.parsedData;
    
    console.log('📝 Initialize:', initData?.result ? '✅ Success' : '❌ Failed');
    
    // Step 2: Send initialized notification (if init was successful)
    if (initData?.result) {
      const notifyResponse = await fetch(`${baseUrl}/mcp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json, text/event-stream',
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'notifications/initialized'
        })
      });
      
      console.log('📝 Initialized notification sent');
    }
    
  } catch (error) {
    console.error('❌ Full flow failed:', error.message);
  }
}

async function runTests() {
  console.log('🧪 Running HTTP MCP Server Tests\n');
  
  await testHealthCheck();
  await testMcpInitialize();
  await testListTools();
  await testWeatherForecast();
  await testWeatherAlerts();
  await testFullMcpFlow();
  
  console.log('\n✨ Test completed!');
  console.log('\n📝 The server is ready for Anthropic MCP Connector:');
  console.log(`   URL: ${baseUrl}/mcp`);
  console.log('   Tools: get-forecast, get-alerts');
  console.log('   Mode: Stateless (perfect for MCP Connector)');
  console.log('   Format: Server-Sent Events (SSE)');
}

runTests().catch(console.error); 