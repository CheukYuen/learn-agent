# analyze_alert 快速使用指南

## 🚀 快速开始

```python
from crisis.workflow import analyze_alert

# 输入告警详情
alert_details = """
告警时间: 2024-01-15 14:30:22
错误信息: Uni bridge call failed with error code 10015
设备型号: iPhone 14 Pro
"""

# 获取智能分析结果
result = analyze_alert(alert_details)
print(result)
```

## 📊 工作原理

`analyze_alert` 采用**两阶段流水线**：

1. **🔍 智能分类**: 自动识别告警类型
2. **🔧 专业分析**: 应用对应的专家分析逻辑

## 🎯 支持的告警类型

| 类型 | 触发关键词 | 专业特性 |
|------|------------|----------|
| **Uni错误** | uni, bridge, 桥接 | 错误码映射 (10001-10019) |
| **JavaScript错误** | JavaScript, JS, TypeError | 堆栈跟踪分析 |
| **API错误** | API, 接口, 服务器, 超时 | HTTP状态分析 |

## 📝 测试示例

```bash
# 测试所有类型
python crisis/example_usage.py

# 测试特定类型  
python crisis/example_usage.py uni
python crisis/example_usage.py javascript
python crisis/example_usage.py backend
```

## 📋 输出格式

```
=== 告警分类结果 ===
类别: uni_error
置信度: 高
分类依据: 发现Uni错误码和移动端特征

=== 专项分析结果 ===
<uni_analysis>
错误码: 10015
原因: 用户权限验证失败
建议: 检查用户登录状态和权限配置
</uni_analysis>
```

## 🔧 核心优势

- ✅ **零配置**: 无需手动指定告警类型
- ✅ **专业分析**: 每种错误都有定制化处理
- ✅ **结构化输出**: XML格式便于集成
- ✅ **高可扩展**: 轻松添加新的告警类型

---

📖 **详细文档**: 查看 `analyze_alert_workflow_guide.md` 获取完整技术细节 