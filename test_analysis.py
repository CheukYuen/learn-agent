#!/usr/bin/env python3
"""
告警分析智能体测试脚本

演示如何使用 AlertAnalysisAgent 来分析各种类型的系统告警
"""

import sys
import os
import json

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crisis import AlertAnalysisAgent

def test_basic_functionality():
    """测试基本功能"""
    print("🔧 初始化告警分析智能体...")
    agent = AlertAnalysisAgent()
    
    print("✅ 智能体初始化成功")
    print(f"📚 知识库包含 {len(agent.knowledge_base)} 个历史事件")
    print(f"🔢 错误码库包含 {len(agent.error_code_mapping)} 个错误码\n")

def test_uni_alert():
    """测试 uni 服务告警"""
    print("=" * 80)
    print("🧪 测试用例 1: uni 服务异常")
    print("=" * 80)
    
    agent = AlertAnalysisAgent()
    
    alert = """
    系统告警: uni服务异常
    时间: 2024-01-15 14:30:00
    错误码: 10015
    告警级别: HIGH
    描述: uni请求超时，连接失败，用户无法登录
    影响: 用户无法正常访问相关功能，业务中断
    服务器: prod-uni-01
    """
    
    print("📝 告警详情:")
    print(alert)
    print("\n🔍 分析结果:")
    result = agent.analyze_alert(alert)
    print(result)
    
    print("\n📊 分析摘要:")
    summary = agent.get_analysis_summary(alert)
    print(json.dumps(summary, indent=2, ensure_ascii=False))

def test_database_alert():
    """测试数据库告警"""
    print("\n" + "=" * 80)
    print("🧪 测试用例 2: 数据库连接异常")
    print("=" * 80)
    
    agent = AlertAnalysisAgent()
    
    alert = """
    系统告警: 数据库连接失败
    时间: 2024-01-15 15:30:00
    错误码: 10006
    告警级别: CRITICAL
    描述: MySQL数据库连接池耗尽，新连接无法建立，查询响应超时
    影响: 系统无法读取用户数据，核心功能异常，大规模影响用户访问
    数据库: prod-mysql-cluster
    连接池状态: 100/100 (已满)
    """
    
    print("📝 告警详情:")
    print(alert)
    print("\n🔍 分析结果:")
    result = agent.analyze_alert(alert)
    print(result)

def test_resource_alert():
    """测试系统资源告警"""
    print("\n" + "=" * 80)
    print("🧪 测试用例 3: 系统资源不足")
    print("=" * 80)
    
    agent = AlertAnalysisAgent()
    
    alert = """
    系统告警: 系统资源不足
    时间: 2024-01-15 16:30:00
    错误码: 10009
    告警级别: WARNING
    描述: 内存使用率达到95%，CPU持续高负载90%，磁盘空间使用率88%，系统响应缓慢
    影响: 系统性能下降，用户体验受影响，部分功能异常
    服务器: prod-app-02
    进程: java应用占用大量内存
    """
    
    print("📝 告警详情:")
    print(alert)
    print("\n🔍 分析结果:")
    result = agent.analyze_alert(alert)
    print(result)

def test_network_alert():
    """测试网络告警"""
    print("\n" + "=" * 80)
    print("🧪 测试用例 4: 网络连接问题")
    print("=" * 80)
    
    agent = AlertAnalysisAgent()
    
    alert = """
    系统告警: 网络连接异常
    时间: 2024-01-15 17:30:00
    错误码: 10101
    告警级别: HIGH
    描述: DNS解析失败，SSL握手超时，负载均衡器检测到多个后端服务不可达
    影响: 用户访问间歇性失败，连接不稳定
    网络设备: 核心交换机，负载均衡器
    """
    
    print("📝 告警详情:")
    print(alert)
    print("\n🔍 分析结果:")
    result = agent.analyze_alert(alert)
    print(result)

def test_custom_configuration():
    """测试自定义配置"""
    print("\n" + "=" * 80)
    print("🧪 测试用例 5: 自定义配置")
    print("=" * 80)
    
    # 自定义配置
    custom_config = {
        "similarity_threshold": 0.5,  # 降低相似度阈值
        "max_historical_matches": 2,  # 限制历史匹配数量
        "log_level": "DEBUG"
    }
    
    # 添加自定义错误码
    custom_error_codes = {
        "99999": "测试错误码",
        "88888": "自定义服务异常"
    }
    
    agent = AlertAnalysisAgent(
        config=custom_config,
        error_code_mapping=custom_error_codes
    )
    
    alert = """
    系统告警: 自定义服务异常
    错误码: 99999
    描述: 这是一个测试告警，用于验证自定义配置功能
    """
    
    print("📝 告警详情:")
    print(alert)
    print("\n🔍 分析结果:")
    result = agent.analyze_alert(alert)
    print(result)

def test_historical_learning():
    """测试历史数据学习功能"""
    print("\n" + "=" * 80)
    print("🧪 测试用例 6: 历史数据学习")
    print("=" * 80)
    
    agent = AlertAnalysisAgent()
    
    # 添加新的历史事件
    new_event = {
        "description": "Redis缓存服务响应缓慢，连接超时",
        "cause": "Redis内存使用率过高，需要清理过期键",
        "solution": "执行FLUSHDB清理缓存，重启Redis服务",
        "prevention": "设置合理的过期时间，实施内存监控",
        "severity": "中",
        "duration": "15分钟"
    }
    
    agent.add_historical_data("incident_005", new_event)
    print("📚 已添加新的历史事件到知识库")
    
    # 测试相似告警
    similar_alert = """
    系统告警: 缓存服务异常
    时间: 2024-01-15 18:30:00
    描述: Redis缓存响应超时，连接建立失败
    影响: 系统性能下降，数据获取缓慢
    """
    
    print("\n📝 告警详情:")
    print(similar_alert)
    print("\n🔍 分析结果（应该匹配新添加的历史事件）:")
    result = agent.analyze_alert(similar_alert)
    print(result)

def main():
    """主函数"""
    print("🚀 告警分析智能体测试开始")
    print("=" * 80)
    
    try:
        # 测试基本功能
        test_basic_functionality()
        
        # 测试各种告警类型
        test_uni_alert()
        test_database_alert() 
        test_resource_alert()
        test_network_alert()
        
        # 测试高级功能
        test_custom_configuration()
        test_historical_learning()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！智能体运行正常")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 