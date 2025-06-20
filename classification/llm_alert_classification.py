#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于LLM的金融APP告警分类Agent
功能：使用Claude大模型智能分类告警为功能异常、性能问题、界面异常三类
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import anthropic
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMAlertClassificationAgent:
    """基于LLM的告警分类智能体"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化LLM分类器
        
        Args:
            api_key: Anthropic API密钥，如果为None则从环境变量读取
            base_url: API基础URL，如果为None则使用中转API
        """
        # 参考test_connect2.py的方式初始化客户端
        self.client = anthropic.Anthropic(
            # 从环境变量读取 API 密钥
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY_PLUS"),
            base_url=base_url or "https://anthropic.claude-plus.top",  # 设置中转 API URL，移除末尾的 /v1 避免路径重复
        )
        
        # 检查API密钥是否设置
        if not (api_key or os.getenv("ANTHROPIC_API_KEY_PLUS")):
            raise ValueError("请设置ANTHROPIC_API_KEY_PLUS环境变量或传入api_key参数")
        
        # 定义分类提示模板
        self.classification_prompt = """
你是一个专业的金融APP告警分类专家。请将以下告警文本分类为以下三个类别之一：

**分类标准：**

1. **功能异常类**：
   - 特征：系统功能无法正常执行、操作失败、错误提示等
   - 示例：登录失败、支付失败、交易失败、系统错误、崩溃闪退等
   - 关键词：失败、无法、错误、异常、崩溃、闪退、中断、超时等

2. **性能问题类**：
   - 特征：系统响应缓慢、加载时间长、操作延迟等
   - 示例：页面加载慢、响应延迟、网络慢、卡顿等
   - 关键词：慢、卡顿、延迟、加载、响应慢、等待、转圈等

3. **界面异常类**：
   - 特征：界面显示问题、布局错误、视觉元素异常等
   - 示例：界面错位、文字重叠、显示空白、布局混乱等
   - 关键词：显示、布局、界面、按钮、页面、错位、重叠、空白等

请分析以下告警文本："{alert_text}"

请以JSON格式返回分析结果，包含以下字段：
{{
    "category": "分类结果（功能异常类/性能问题类/界面异常类/未知类型）",
    "confidence": "置信度（0.0-1.0之间的浮点数）",
    "reason": "分类原因的详细说明",
    "keywords_found": ["识别到的关键词列表"],
    "analysis": "详细的分析过程"
}}

注意：
- 如果告警文本不明确或无法归类，请分类为"未知类型"
- 置信度应该基于文本的明确程度和关键词匹配度
- 分类原因要具体说明为什么选择这个类别
"""

    def classify_alert(self, alert_text: str) -> Dict:
        """
        使用LLM分类单条告警
        
        Args:
            alert_text: 告警文本描述
            
        Returns:
            分类结果字典
        """
        start_time = time.time()
        
        try:
            # 构建提示
            prompt = self.classification_prompt.format(alert_text=alert_text)
            
            # 调用Claude API
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=0.1,  # 低温度确保结果稳定
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            
            # 解析响应
            response_text = message.content[0].text
            
            # 尝试解析JSON响应
            try:
                # 提取JSON部分（可能包含其他文本）
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    llm_result = json.loads(json_str)
                else:
                    raise json.JSONDecodeError("No JSON found", response_text, 0)
                    
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用备用方案
                llm_result = self._parse_fallback_response(response_text, alert_text)
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 构建标准化结果
            result = {
                "alert_text": alert_text,
                "category": llm_result.get("category", "未知类型"),
                "confidence": float(llm_result.get("confidence", 0.5)),
                "reason": llm_result.get("reason", "LLM分析结果"),
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": datetime.now().isoformat(),
                "llm_analysis": llm_result.get("analysis", ""),
                "keywords_found": llm_result.get("keywords_found", []),
                "raw_response": response_text
            }
            
            return result
            
        except Exception as e:
            # 错误处理
            response_time = time.time() - start_time
            return {
                "alert_text": alert_text,
                "category": "未知类型",
                "confidence": 0.0,
                "reason": f"LLM分析失败: {str(e)}",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _parse_fallback_response(self, response_text: str, alert_text: str) -> Dict:
        """
        当JSON解析失败时的备用解析方案
        """
        # 简单的文本解析逻辑
        response_lower = response_text.lower()
        
        if "功能异常" in response_text:
            category = "功能异常类"
        elif "性能问题" in response_text:
            category = "性能问题类"
        elif "界面异常" in response_text:
            category = "界面异常类"
        else:
            category = "未知类型"
        
        return {
            "category": category,
            "confidence": 0.6,
            "reason": "基于文本内容的备用分析",
            "analysis": response_text,
            "keywords_found": []
        }
    
    def batch_classify(self, alerts: List[str], batch_size: int = 5) -> List[Dict]:
        """
        批量分类告警（考虑API限制，分批处理）
        
        Args:
            alerts: 告警文本列表
            batch_size: 批处理大小，避免API超限
            
        Returns:
            分类结果列表
        """
        results = []
        
        for i in range(0, len(alerts), batch_size):
            batch = alerts[i:i + batch_size]
            
            for alert in batch:
                result = self.classify_alert(alert)
                results.append(result)
                
                # 添加延迟避免API限制
                time.sleep(0.1)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> Dict:
        """生成分类统计报告"""
        if not results:
            return {"error": "无分类结果"}
        
        # 统计各类别数量
        category_counts = {}
        confidence_scores = []
        response_times = []
        error_count = 0
        
        for result in results:
            category = result["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
            confidence_scores.append(result["confidence"])
            response_times.append(result["response_time_ms"])
            
            if "error" in result:
                error_count += 1
        
        # 计算统计指标
        total_alerts = len(results)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
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
            ) if confidence_scores else 0,
            "error_rate": round(error_count / total_alerts * 100, 1),
            "success_rate": round((total_alerts - error_count) / total_alerts * 100, 1)
        }
    
    def compare_with_keyword_method(self, alerts: List[str], 
                                  keyword_agent) -> Dict:
        """
        与关键词方法对比分析
        
        Args:
            alerts: 测试告警列表
            keyword_agent: 关键词分类器实例
            
        Returns:
            对比分析结果
        """
        llm_results = self.batch_classify(alerts)
        keyword_results = keyword_agent.batch_classify(alerts)
        
        agreement_count = 0
        differences = []
        
        for i, (llm_res, kw_res) in enumerate(zip(llm_results, keyword_results)):
            if llm_res["category"] == kw_res["category"]:
                agreement_count += 1
            else:
                differences.append({
                    "alert_text": alerts[i],
                    "llm_category": llm_res["category"],
                    "keyword_category": kw_res["category"],
                    "llm_confidence": llm_res["confidence"],
                    "keyword_confidence": kw_res["confidence"]
                })
        
        return {
            "total_comparisons": len(alerts),
            "agreement_count": agreement_count,
            "agreement_rate": round(agreement_count / len(alerts) * 100, 1),
            "differences": differences,
            "llm_avg_confidence": round(
                sum(r["confidence"] for r in llm_results) / len(llm_results), 2
            ),
            "keyword_avg_confidence": round(
                sum(r["confidence"] for r in keyword_results) / len(keyword_results), 2
            )
        }

# 测试数据（与原版保持一致）
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

def test_llm_classification_accuracy(agent: LLMAlertClassificationAgent, 
                                   test_data: List[Tuple[str, str]]) -> float:
    """
    测试LLM分类准确率
    
    Args:
        agent: LLM分类器实例
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
    """主函数 - 演示LLM分类器完整流程"""
    print("=" * 60)
    print("基于LLM的金融APP告警分类Agent Demo")
    print("=" * 60)
    
    try:
        # 创建LLM分类器实例
        llm_agent = LLMAlertClassificationAgent()
        
        # 1. 单条告警分类演示
        print("\n1. LLM单条告警分类演示:")
        print("-" * 40)
        
        sample_alert = "用户反馈点击买入按钮后页面无响应，等待30秒后App闪退"
        result = llm_agent.classify_alert(sample_alert)
        
        print(f"告警内容: {sample_alert}")
        print(f"LLM分类结果: {result['category']}")
        print(f"置信度: {result['confidence']}")
        print(f"分类原因: {result['reason']}")
        print(f"响应时间: {result['response_time_ms']}ms")
        print(f"关键词: {result.get('keywords_found', [])}")
        
        # 2. 批量分类演示
        print("\n2. LLM批量分类演示:")
        print("-" * 40)
        
        # 只处理前5条以节省API调用
        batch_results = llm_agent.batch_classify(SAMPLE_ALERTS[:5])
        
        for i, result in enumerate(batch_results, 1):
            print(f"{i}. {result['alert_text'][:30]}...")
            print(f"   分类: {result['category']} (置信度: {result['confidence']})")
            print(f"   原因: {result['reason']}")
        
        # 3. 生成统计报告
        print("\n3. LLM分类统计报告:")
        print("-" * 40)
        
        report = llm_agent.generate_report(batch_results)
        print(f"总告警数: {report['total_alerts']}")
        print(f"平均置信度: {report['avg_confidence']}")
        print(f"平均响应时间: {report['avg_response_time_ms']}ms")
        print(f"高置信度比例: {report['high_confidence_rate']}%")
        print(f"成功率: {report['success_rate']}%")
        
        print("\n类别分布:")
        for category, count in report['category_distribution'].items():
            percentage = report['category_percentages'][category]
            print(f"  {category}: {count}条 ({percentage}%)")
        
        # 4. 保存结果
        print("\n4. 保存LLM分类结果:")
        print("-" * 40)
        
        # 保存详细结果
        with open('llm_classification_results.json', 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, ensure_ascii=False, indent=2)
        
        # 保存统计报告
        with open('llm_classification_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("LLM结果已保存到 llm_classification_results.json")
        print("LLM报告已保存到 llm_classification_report.json")
        
        # 5. 对比分析（如果有关键词版本）
        print("\n5. 方法对比分析:")
        print("-" * 40)
        
        try:
            from alert_classification_demo_code import AlertClassificationAgent
            keyword_agent = AlertClassificationAgent()
            
            # 对比前3条告警
            comparison = llm_agent.compare_with_keyword_method(
                SAMPLE_ALERTS[:3], keyword_agent
            )
            
            print(f"对比样本数: {comparison['total_comparisons']}")
            print(f"分类一致率: {comparison['agreement_rate']}%")
            print(f"LLM平均置信度: {comparison['llm_avg_confidence']}")
            print(f"关键词平均置信度: {comparison['keyword_avg_confidence']}")
            
            if comparison['differences']:
                print("\n分类差异:")
                for diff in comparison['differences']:
                    print(f"  告警: {diff['alert_text'][:40]}...")
                    print(f"  LLM: {diff['llm_category']} ({diff['llm_confidence']})")
                    print(f"  关键词: {diff['keyword_category']} ({diff['keyword_confidence']})")
            
        except ImportError:
            print("无法导入关键词分类器，跳过对比分析")
        
    except Exception as e:
        print(f"Error: {e}")
        print("请检查API密钥设置和网络连接")
    
    print("\n" + "=" * 60)
    print("LLM分类Demo运行完成！")
    print("=" * 60)

if __name__ == "__main__":
    main() 