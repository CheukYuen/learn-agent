#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融APP告警分类Agent Demo
功能：自动将告警分为功能异常、性能问题、界面异常三类
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd

class AlertClassificationAgent:
    """告警分类智能体"""
    
    def __init__(self):
        # 定义分类规则
        self.classification_rules = {
            "功能异常类": {
                "keywords": [
                    "失败", "无法", "错误", "异常", "崩溃", "闪退", "中断", 
                    "超时", "连接失败", "支付失败", "交易失败", "登录失败",
                    "下单失败", "提交失败", "验证失败", "授权失败"
                ],
                "patterns": [
                    r".*失败.*", r".*无法.*", r".*错误.*", r".*异常.*",
                    r".*崩溃.*", r".*闪退.*", r".*中断.*"
                ]
            },
            "性能问题类": {
                "keywords": [
                    "慢", "卡顿", "延迟", "超时", "加载", "响应慢", 
                    "网络慢", "打开慢", "反应慢", "等待", "转圈",
                    "加载中", "请稍候", "网络延迟"
                ],
                "patterns": [
                    r".*慢.*", r".*卡顿.*", r".*延迟.*", r".*加载.*",
                    r".*等待.*", r".*转圈.*", r".*超时.*"
                ]
            },
            "界面异常类": {
                "keywords": [
                    "显示", "布局", "界面", "按钮", "页面", "图片", "文字",
                    "错位", "重叠", "缺失", "空白", "乱码", "模糊",
                    "变形", "截断", "遮挡", "颜色", "字体"
                ],
                "patterns": [
                    r".*显示.*", r".*布局.*", r".*界面.*", r".*按钮.*",
                    r".*页面.*", r".*错位.*", r".*重叠.*", r".*空白.*"
                ]
            }
        }
    
    def classify_alert(self, alert_text: str) -> Dict:
        """
        分类单条告警
        
        Args:
            alert_text: 告警文本描述
            
        Returns:
            分类结果字典
        """
        start_time = time.time()
        
        # 预处理文本
        text = alert_text.lower().strip()
        
        # 计算每个类别的匹配分数
        scores = {}
        details = {}
        
        for category, rules in self.classification_rules.items():
            keyword_matches = 0
            pattern_matches = 0
            matched_keywords = []
            
            # 关键词匹配
            for keyword in rules["keywords"]:
                if keyword in text:
                    keyword_matches += 1
                    matched_keywords.append(keyword)
            
            # 正则匹配
            for pattern in rules["patterns"]:
                if re.search(pattern, text):
                    pattern_matches += 1
            
            # 计算综合分数
            score = (keyword_matches * 0.7) + (pattern_matches * 0.3)
            scores[category] = score
            details[category] = {
                "keyword_matches": keyword_matches,
                "pattern_matches": pattern_matches,
                "matched_keywords": matched_keywords
            }
        
        # 找出最高分类别
        if max(scores.values()) == 0:
            category = "未知类型"
            confidence = 0.3
            reason = "未匹配到已知关键词"
        else:
            category = max(scores, key=scores.get)
            max_score = scores[category]
            confidence = min(0.95, 0.5 + (max_score * 0.1))  # 基础置信度0.5，根据匹配度调整
            reason = f"匹配到关键词: {', '.join(details[category]['matched_keywords'][:3])}"
        
        # 计算响应时间
        response_time = time.time() - start_time
        
        return {
            "alert_text": alert_text,
            "category": category,
            "confidence": round(confidence, 2),
            "reason": reason,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
    
    def batch_classify(self, alerts: List[str]) -> List[Dict]:
        """批量分类告警"""
        results = []
        for alert in alerts:
            result = self.classify_alert(alert)
            results.append(result)
        return results
    
    def generate_report(self, results: List[Dict]) -> Dict:
        """生成分类统计报告"""
        if not results:
            return {"error": "无分类结果"}
        
        # 统计各类别数量
        category_counts = {}
        confidence_scores = []
        response_times = []
        
        for result in results:
            category = result["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
            confidence_scores.append(result["confidence"])
            response_times.append(result["response_time_ms"])
        
        # 计算统计指标
        total_alerts = len(results)
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_alerts": total_alerts,
            "category_distribution": category_counts,
            "category_percentages": {
                k: round(v/total_alerts*100, 1) 
                for k, v in category_counts.items()
            },
            "avg_confidence": round(avg_confidence, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "high_confidence_rate": round(
                len([s for s in confidence_scores if s >= 0.8]) / total_alerts * 100, 1
            )
        }

# 测试数据
SAMPLE_ALERTS = [
    "用户反馈点击买入按钮后页面无响应，等待30秒后App闪退",
    "交易页面加载超过1分钟，用户无法查看持仓信息",
    "支付密码输入后提示网络异常，无法完成支付",
    "首页股票价格显示错位，数字重叠无法看清",
    "登录时指纹识别失败，提示系统错误",
    "K线图显示空白，页面布局混乱",
    "转账功能响应很慢，点击后需要等待很久",
    "用户头像显示不正常，文字被截断",
    "下单时提示余额不足，但实际余额充足",
    "App启动后卡在加载页面，无法进入主界面"
]

def test_classification_accuracy(agent: AlertClassificationAgent, 
                               test_data: List[Tuple[str, str]]) -> float:
    """
    测试分类准确率
    
    Args:
        agent: 分类器实例
        test_data: [(告警文本, 正确分类), ...] 格式的测试数据
        
    Returns:
        准确率 (0-1)
    """
    correct = 0
    total = len(test_data)
    
    for alert_text, correct_category in test_data:
        result = agent.classify_alert(alert_text)
        if result["category"] == correct_category:
            correct += 1
    
    return correct / total

def main():
    """主函数 - 演示完整流程"""
    print("=" * 50)
    print("金融APP告警分类Agent Demo")
    print("=" * 50)
    
    # 创建分类器实例
    agent = AlertClassificationAgent()
    
    # 1. 单条告警分类演示
    print("\n1. 单条告警分类演示:")
    print("-" * 30)
    
    sample_alert = "用户反馈点击买入按钮后页面无响应，等待30秒后App闪退"
    result = agent.classify_alert(sample_alert)
    
    print(f"告警内容: {sample_alert}")
    print(f"分类结果: {result['category']}")
    print(f"置信度: {result['confidence']}")
    print(f"分类原因: {result['reason']}")
    print(f"响应时间: {result['response_time_ms']}ms")
    
    # 2. 批量分类演示
    print("\n2. 批量分类演示:")
    print("-" * 30)
    
    batch_results = agent.batch_classify(SAMPLE_ALERTS)
    
    for i, result in enumerate(batch_results[:5], 1):  # 只显示前5条
        print(f"{i}. {result['alert_text'][:30]}...")
        print(f"   分类: {result['category']} (置信度: {result['confidence']})")
    
    # 3. 生成统计报告
    print("\n3. 统计报告:")
    print("-" * 30)
    
    report = agent.generate_report(batch_results)
    print(f"总告警数: {report['total_alerts']}")
    print(f"平均置信度: {report['avg_confidence']}")
    print(f"平均响应时间: {report['avg_response_time_ms']}ms")
    print(f"高置信度比例: {report['high_confidence_rate']}%")
    
    print("\n类别分布:")
    for category, count in report['category_distribution'].items():
        percentage = report['category_percentages'][category]
        print(f"  {category}: {count}条 ({percentage}%)")
    
    # 4. 准确率测试（需要人工标注的测试数据）
    print("\n4. 准确率测试:")
    print("-" * 30)
    
    # 模拟测试数据（实际使用时需要人工标注）
    test_data = [
        ("用户反馈点击买入按钮后页面无响应，等待30秒后App闪退", "功能异常类"),
        ("交易页面加载超过1分钟，用户无法查看持仓信息", "性能问题类"),
        ("首页股票价格显示错位，数字重叠无法看清", "界面异常类"),
        ("支付密码输入后提示网络异常，无法完成支付", "功能异常类"),
        ("App启动后卡在加载页面，无法进入主界面", "性能问题类")
    ]
    
    accuracy = test_classification_accuracy(agent, test_data)
    print(f"分类准确率: {accuracy*100:.1f}%")
    
    # 5. 性能测试
    print("\n5. 性能测试:")
    print("-" * 30)
    
    # 测试响应时间
    response_times = [result['response_time_ms'] for result in batch_results]
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    
    print(f"平均响应时间: {avg_time:.2f}ms")
    print(f"最大响应时间: {max_time:.2f}ms")
    print(f"性能目标(3秒): {'✅ 通过' if max_time < 3000 else '❌ 未通过'}")
    
    # 6. 保存结果到文件
    print("\n6. 保存结果:")
    print("-" * 30)
    
    # 保存详细结果
    with open('classification_results.json', 'w', encoding='utf-8') as f:
        json.dump(batch_results, f, ensure_ascii=False, indent=2)
    
    # 保存统计报告
    with open('classification_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("结果已保存到 classification_results.json")
    print("报告已保存到 classification_report.json")
    
    print("\n" + "=" * 50)
    print("Demo运行完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
