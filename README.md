# Crisis Agent - 智能告警分析系统

## 📋 项目简介

Crisis Agent 是一个基于提示词模板的智能告警分析系统，能够自动分析系统告警并提供全面的分析报告，包括潜在原因、影响评估和针对性的响应措施建议。

## ✨ 核心功能

### 🔍 智能分析能力
- **错误码识别**: 自动识别并解析告警中的错误码，提供详细的错误含义
- **关键词分析**: 基于预定义词典分析告警内容，识别可能的问题类型
- **历史事件匹配**: 与历史知识库进行相似度比较，提供参考案例
- **系统组件识别**: 自动识别受影响的系统组件和服务

### 📊 影响评估
- **严重程度分级**: 根据关键词自动评估告警的严重程度（严重/高/中/低/信息）
- **受影响系统**: 识别可能受到影响的系统组件和服务
- **级联影响分析**: 评估潜在的连锁反应和业务影响

### 🎯 智能响应建议
- **即时措施**: 提供立即可执行的应急处理步骤
- **长期措施**: 建议预防性措施和系统改进方案
- **模板化响应**: 针对不同类型的问题提供专业的响应模板

## 🏗️ 系统架构

```
crisis-agent/
├── crisis/                    # 核心包
│   ├── __init__.py            # 包初始化
│   ├── analysis.py            # 主分析引擎
│   ├── config.py              # 配置文件
│   └── analysis-prompt.md     # 原始提示词模板
├── test_analysis.py           # 测试脚本
└── README.md                  # 项目文档
```

## 🚀 快速开始

### 基本使用

```python
from crisis import AlertAnalysisAgent

# 初始化智能体
agent = AlertAnalysisAgent()

# 分析告警
alert = """
系统告警: aladdin服务异常
时间: 2024-01-15 14:30:00
错误码: 10015
描述: aladdin请求超时，连接失败
影响: 用户无法正常访问相关功能
"""

result = agent.analyze_alert(alert)
print(result)
```

### 自定义配置

```python
# 自定义配置
custom_config = {
    "similarity_threshold": 0.7,  # 历史事件相似度阈值
    "max_historical_matches": 3,  # 最大历史匹配数量
    "log_level": "DEBUG"
}

# 自定义错误码
custom_error_codes = {
    "99999": "自定义错误码",
    "88888": "特殊服务异常"
}

agent = AlertAnalysisAgent(
    config=custom_config,
    error_code_mapping=custom_error_codes
)
```

### 添加历史数据

```python
# 添加新的历史事件
new_event = {
    "description": "Redis缓存服务响应缓慢",
    "cause": "Redis内存使用率过高",
    "solution": "清理缓存，重启服务",
    "prevention": "设置内存监控",
    "severity": "中",
    "duration": "15分钟"
}

agent.add_historical_data("incident_005", new_event)
```

## 📝 输出格式

系统输出采用结构化的XML格式：

```xml
<analysis>
<possible_causes>
• 错误码 10015: aladdin请求失败
• 关键词分析 - 超时: 网络连接超时或服务响应时间过长
• 关键词分析 - 连接失败: 网络连接问题或目标服务不可用
</possible_causes>

<impact_assessment>
严重程度: 高
受影响的系统/服务: aladdin, 网络
潜在级联影响: 高风险 - 可能导致业务中断
影响范围: 可能影响最终用户和业务流程
</impact_assessment>

<response_measures>
即时措施:
1. 检查aladdin服务状态和健康检查端点
2. 查看aladdin服务日志，识别错误模式
3. 验证aladdin服务依赖的下游服务状态

长期措施:
1. 优化aladdin服务的错误处理和重试机制
2. 实施服务熔断和降级策略
3. 增强aladdin服务监控和告警
</response_measures>
</analysis>
```

## 🔧 配置说明

### 错误码映射

支持多种错误码类型：
- **系统错误** (10000-10099): 内部错误、参数错误、权限问题等
- **网络错误** (10100-10199): DNS、SSL、代理服务器等网络相关问题
- **数据库错误** (10200-10299): 连接、查询、锁等数据库相关问题
- **业务逻辑错误** (10300-10399): 认证、授权、业务规则等问题

### 严重程度分级

- **严重**: 系统崩溃、服务中断、数据丢失
- **高**: 大规模影响、核心功能异常、用户无法访问
- **中**: 性能下降、部分功能异常、连接不稳定
- **低**: 轻微影响、个别用户反馈、功能降级
- **信息**: 警告、提醒、建议、优化类信息

### 响应模板

针对不同问题类型提供专业响应模板：
- **aladdin服务**: aladdin相关问题的专业处理流程
- **数据库**: 数据库连接、性能、锁等问题的处理方案
- **网络**: 网络连通性、DNS、SSL等问题的排查步骤
- **资源**: CPU、内存、磁盘等资源问题的优化建议

## 🧪 运行测试

```bash
# 运行完整测试套件
python test_analysis.py

# 运行基础功能测试
python -c "from crisis import AlertAnalysisAgent; agent = AlertAnalysisAgent(); print('✅ 初始化成功')"
```

测试覆盖以下场景：
1. **aladdin服务异常**: 测试aladdin服务相关告警的分析
2. **数据库连接异常**: 测试数据库问题的识别和响应
3. **系统资源不足**: 测试资源类问题的分析
4. **网络连接问题**: 测试网络相关问题的处理
5. **自定义配置**: 测试配置的灵活性
6. **历史数据学习**: 测试知识库的动态更新

## 📈 高级功能

### 分析摘要

获取结构化的分析摘要：

```python
summary = agent.get_analysis_summary(alert_details)
# 返回JSON格式的摘要信息
{
  "severity": "高",
  "affected_systems": ["aladdin", "网络"],
  "cause_count": 4,
  "has_historical_match": false,
  "error_codes": ["10015"],
  "timestamp": "2024-01-15T14:30:00"
}
```

### 实时日志

支持可配置的日志级别：
- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息

### 扩展性

- **插件式架构**: 支持自定义分析模块
- **配置驱动**: 通过配置文件灵活调整行为
- **知识库更新**: 支持动态添加和更新历史数据
- **多语言支持**: 支持中英文混合分析

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [项目主页](https://github.com/crisis-agent)
- [问题反馈](https://github.com/crisis-agent/issues)
- [更新日志](CHANGELOG.md)

## 👥 作者

- **Crisis Agent Team** - *初始开发* - [GitHub](https://github.com/crisis-agent)

## 🙏 致谢

感谢所有为这个项目贡献代码、提出建议和报告问题的开发者们！ 