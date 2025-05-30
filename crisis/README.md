# 智能告警分析系统

## 概述

这是一个基于LLM的智能告警分析系统，能够自动分类告警并提供针对性的分析和解决方案。系统采用分层处理架构，首先对告警进行分类，然后根据不同类别应用专门的分析逻辑。

## 系统架构

### 工作流程

1. **告警分类** - 使用 `alert-classification-prompt.md` 将告警分为三个类别
2. **专项分析** - 根据分类结果调用对应的专门提示词
3. **结果整合** - 将分类结果和分析结果合并输出

### 支持的告警类别

#### 1. JavaScript Error (`javascript_error`)
- **适用场景**: 前端JavaScript运行时错误、浏览器兼容性问题
- **处理方式**: 详细分析错误类型、堆栈信息，并标识需要代码调查的范围
- **输出格式**: 包含错误类型、堆栈分析、原因分析、代码调查建议等

#### 2. Aladdin Error (`aladdin_error`)  
- **适用场景**: Aladdin JS Bridge相关错误
- **处理方式**: 专门解释错误码含义，提供快速修复方案
- **特色功能**: 内置常见错误码映射（10001-10019）
- **输出格式**: 错误码解释、可能原因、快速修复、升级建议

#### 3. Backend API Error (`backend_api_error`)
- **适用场景**: 后端接口异常、服务器错误、数据库问题
- **处理方式**: 分析HTTP状态码、服务影响范围、根因分析
- **输出格式**: 错误分类、状态码分析、影响评估、根因分析、代码调查范围

## 文件说明

### 核心文件

- `workflow.py` - 主要工作流逻辑
  - `analyze_alert()` - 新增的告警分析主函数
  - `route()` - 原有的通用路由函数

- `util.py` - 工具函数
- `config.py` - 配置管理

### 提示词模板

- `alert-classification-prompt.md` - 告警分类提示词
- `aladdin-error-prompt.md` - Aladdin错误专项分析
- `javascript-error-prompt.md` - JavaScript错误专项分析  
- `backend-api-error-prompt.md` - 后端API错误专项分析
- `analysis-prompt.md` - 通用分析提示词（备用）

### 示例和测试

- `example_usage.py` - 使用示例和测试用例

## 使用方法

### 基本用法

```python
from workflow import analyze_alert

# 分析告警
alert_details = """
告警时间: 2024-01-15 14:30:22
错误信息: Aladdin bridge call failed with error code 10015
...
"""

result = analyze_alert(alert_details)
print(result)
```

### 运行示例

```bash
# 运行所有测试用例
python example_usage.py

# 运行特定类型测试
python example_usage.py aladdin     # Aladdin错误测试
python example_usage.py javascript  # JavaScript错误测试
python example_usage.py backend     # 后端API错误测试
```

## 输出格式

系统输出包含两个主要部分：

### 1. 告警分类结果
```
=== 告警分类结果 ===
类别: aladdin_error
置信度: 高
分类依据: 告警信息中包含"Aladdin bridge"和错误码"10015"...
```

### 2. 专项分析结果
根据不同类别，输出相应的结构化分析：

- **Aladdin错误**: 错误码解释、原因分析、快速修复
- **JavaScript错误**: 错误类型、堆栈分析、代码调查建议
- **后端API错误**: 状态码分析、影响评估、根因分析

## 扩展功能

### 待实现功能

1. **代码库扫描** - 对JavaScript错误和后端API错误进行代码库扫描
2. **历史案例匹配** - 基于相似告警的历史处理方案
3. **自动化修复建议** - 基于代码分析的自动化修复建议

### 自定义扩展

可以通过以下方式扩展系统：

1. **添加新的告警类别**
   - 在 `alert-classification-prompt.md` 中添加新类别
   - 创建对应的专项分析提示词
   - 在 `analyze_alert()` 函数中添加处理逻辑

2. **优化现有分析逻辑**
   - 修改对应的提示词模板
   - 调整分类规则和关键词

## 配置说明

系统配置主要在 `config.py` 中管理，包括：
- LLM服务配置
- 提示词路径配置
- 日志和监控配置

## 注意事项

1. 确保所有提示词文件使用UTF-8编码
2. 分类置信度低时，系统会回退到通用分析
3. 代码库扫描功能需要额外配置代码仓库访问权限
4. 建议定期更新错误码映射库以保持准确性 