#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
告警分类方法对比测试
对比关键词+正则方法 vs LLM大模型方法
"""

import os
from dotenv import load_dotenv
from alert_classification_demo_code import AlertClassificationAgent
from llm_alert_classification import LLMAlertClassificationAgent

# 加载环境变量
load_dotenv()

# 测试告警样本
TEST_ALERTS = [
    "用户反馈点击买入按钮后页面无响应，等待30秒后App闪退",
    "交易页面加载超过1分钟，用户无法查看持仓信息", 
    "首页股票价格显示错位，数字重叠无法看清",
]

def main():
    """运行对比测试"""
    print("=" * 60)
    print("告警分类方法对比测试")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv("ANTHROPIC_API_KEY_PLUS"):
        print("❌ 错误：请先设置ANTHROPIC_API_KEY_PLUS环境变量")
        print("export ANTHROPIC_API_KEY_PLUS=your_api_key")
        return
    
    try:
        # 创建分类器实例
        print("\n初始化分类器...")
        keyword_agent = AlertClassificationAgent()
        llm_agent = LLMAlertClassificationAgent()
        
        print("\n" + "=" * 60)
        print("逐条对比分析")
        print("=" * 60)
        
        for i, alert in enumerate(TEST_ALERTS, 1):
            print(f"\n📋 测试样本 {i}:")
            print(f"告警内容: {alert}")
            print("-" * 50)
            
            # 关键词方法分类
            keyword_result = keyword_agent.classify_alert(alert)
            print(f"🔍 关键词方法:")
            print(f"  分类: {keyword_result['category']}")
            print(f"  置信度: {keyword_result['confidence']}")
            print(f"  原因: {keyword_result['reason']}")
            print(f"  响应时间: {keyword_result['response_time_ms']}ms")
            
            # LLM方法分类  
            llm_result = llm_agent.classify_alert(alert)
            print(f"\n🤖 LLM方法:")
            print(f"  分类: {llm_result['category']}")
            print(f"  置信度: {llm_result['confidence']}")
            print(f"  原因: {llm_result['reason']}")
            print(f"  响应时间: {llm_result['response_time_ms']}ms")
            
            # 对比结果
            if keyword_result['category'] == llm_result['category']:
                print(f"\n✅ 分类一致: {keyword_result['category']}")
            else:
                print(f"\n⚠️  分类不一致:")
                print(f"   关键词: {keyword_result['category']}")
                print(f"   LLM: {llm_result['category']}")
        
        # 生成整体对比报告
        print("\n" + "=" * 60)
        print("整体对比分析")
        print("=" * 60)
        
        comparison = llm_agent.compare_with_keyword_method(TEST_ALERTS, keyword_agent)
        
        print(f"📊 统计结果:")
        print(f"  测试样本数: {comparison['total_comparisons']}")
        print(f"  分类一致率: {comparison['agreement_rate']}%")
        print(f"  LLM平均置信度: {comparison['llm_avg_confidence']}")
        print(f"  关键词平均置信度: {comparison['keyword_avg_confidence']}")
        
        if comparison['differences']:
            print(f"\n📝 分类差异详情:")
            for diff in comparison['differences']:
                print(f"  告警: {diff['alert_text'][:40]}...")
                print(f"    LLM: {diff['llm_category']} ({diff['llm_confidence']})")
                print(f"    关键词: {diff['keyword_category']} ({diff['keyword_confidence']})")
        else:
            print(f"\n✅ 所有样本分类完全一致！")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        print("请检查API密钥设置和网络连接")

if __name__ == "__main__":
    main() 