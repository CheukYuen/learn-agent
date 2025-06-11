# Browser Use Demo with DeepSeek R1

这是一个使用 DeepSeek R1 模型驱动的浏览器自动化演示项目。

## 项目概述

本项目展示了如何使用 DeepSeek R1 大语言模型结合 browser-use 框架来实现智能浏览器自动化。该演示可以让 AI 代理自动执行复杂的浏览器操作，如搜索商品、比较价格等。

## 功能特性

- 🤖 使用 DeepSeek R1 模型进行智能决策
- 🌐 自动化浏览器操作
- 🛒 电商网站自动化（如 Amazon 搜索、排序、获取价格）
- 📊 结构化数据提取

## 环境要求

- Python >= 3.11
- 有效的 DeepSeek API 密钥

## 安装指南

### 1. 克隆或创建项目

```bash
mkdir browser-use-demo
cd browser-use-demo
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 或使用 conda
conda create -n browser-use python=3.11
conda activate browser-use
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Playwright 浏览器

```bash
playwright install chromium --with-deps --no-shell
```

### 5. 配置环境变量

创建 `.env` 文件并添加您的 API 密钥：

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## 使用方法

运行演示脚本：

```bash
python deepseek-r1.py
```

## 代码说明

- `deepseek-r1.py` - 主演示脚本
- 使用 DeepSeek R1 模型 (`deepseek-reasoner`)
- 配置了基本的浏览器自动化任务

## 注意事项

1. **API 密钥**: 确保您有有效的 DeepSeek API 密钥
2. **网络连接**: 需要稳定的网络连接访问 DeepSeek API
3. **浏览器权限**: 某些网站可能有反自动化措施
4. **使用限制**: 请遵守网站的使用条款和 API 使用限制

## 故障排除

### 常见问题

1. **ImportError**: 确保所有依赖都已正确安装
2. **API 错误**: 检查 DeepSeek API 密钥是否正确
3. **浏览器启动失败**: 确保 Playwright 浏览器已正确安装

### 调试技巧

- 启用详细日志输出
- 检查网络连接
- 验证环境变量设置

## 相关资源

- [DeepSeek API 文档](https://api.deepseek.com/)
- [Browser-use GitHub](https://github.com/browser-use/browser-use)
- [LangChain DeepSeek 集成](https://python.langchain.com/docs/integrations/chat/deepseek/)
- [Playwright 文档](https://playwright.dev/python/)

## 许可证

MIT License 