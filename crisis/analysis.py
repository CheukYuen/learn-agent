import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# 导入配置
from .config import (
    ERROR_CODE_MAPPING, KNOWLEDGE_BASE, SEVERITY_KEYWORDS, 
    SYSTEM_COMPONENTS, DEFAULT_CONFIG, RESPONSE_TEMPLATES
)

class AlertAnalysisAgent:
    """
    智能告警分析代理
    负责分析和响应系统告警，提供全面的告警分析，包括潜在原因、影响评估和针对性的响应措施
    """
    
    def __init__(self, knowledge_base: Optional[Dict] = None, 
                 error_code_mapping: Optional[Dict] = None,
                 config: Optional[Dict] = None,
                 code_repository: Optional[Any] = None):
        """
        初始化告警分析代理
        
        Args:
            knowledge_base: 历史数据知识库
            error_code_mapping: 错误码映射库
            config: 配置参数
            code_repository: 代码仓库访问接口
        """
        self.knowledge_base = knowledge_base or KNOWLEDGE_BASE
        self.error_code_mapping = error_code_mapping or ERROR_CODE_MAPPING
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.code_repository = code_repository
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config.get('log_level', 'INFO')))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def analyze_alert(self, alert_details: str) -> str:
        """
        分析告警的主要方法
        
        Args:
            alert_details: 告警详细信息
            
        Returns:
            分析结果（XML格式）
        """
        try:
            self.logger.info("开始分析告警")
            
            # 1. 识别可能的触发原因
            possible_causes = self._identify_possible_causes(alert_details)
            
            # 2. 评估影响范围
            impact_assessment = self._assess_impact(alert_details)
            
            # 3. 提供针对性的响应措施
            response_measures = self._generate_response_measures(alert_details, possible_causes)
            
            # 格式化输出
            result = self._format_analysis_result(possible_causes, impact_assessment, response_measures)
            self.logger.info("告警分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"告警分析过程中发生错误: {str(e)}")
            return self._format_error_response(str(e))
    
    def _identify_possible_causes(self, alert_details: str) -> List[str]:
        """识别可能的触发原因"""
        causes = []
        
        # 提取和解析错误码
        error_codes = self._extract_error_codes(alert_details)
        for code in error_codes:
            if code in self.error_code_mapping:
                error_meaning = self.error_code_mapping[code]
                causes.append(f"错误码 {code}: {error_meaning}")
                self.logger.debug(f"识别错误码: {code} - {error_meaning}")
        
        # 关键词分析
        keywords_analysis = self._analyze_keywords(alert_details)
        causes.extend(keywords_analysis)
        
        # 历史数据比较
        historical_analysis = self._compare_with_history(alert_details)
        causes.extend(historical_analysis)
        
        # 系统组件分析
        component_analysis = self._analyze_system_components(alert_details)
        causes.extend(component_analysis)
        
        # 如果没有找到具体原因，提供通用分析
        if not causes:
            causes.append("需要进一步调查：告警信息中未发现已知错误模式")
        
        return causes
    
    def _extract_error_codes(self, alert_details: str) -> List[str]:
        """从告警详情中提取错误码"""
        # 匹配数字错误码模式（如：10015, 错误码:10001等）
        patterns = [
            r'(?:错误码[:：]\s*)?(\d{4,6})',
            r'error\s*code[:：]?\s*(\d{4,6})',
            r'code[:：]?\s*(\d{4,6})',
            r'\b(\d{5})\b'  # 匹配独立的5位数字
        ]
        
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, alert_details, re.IGNORECASE))
        
        return list(set(matches))  # 去重
    
    def _analyze_keywords(self, alert_details: str) -> List[str]:
        """基于关键词分析可能原因"""
        keyword_mapping = {
            "超时": "网络连接超时或服务响应时间过长",
            "timeout": "服务响应超时",
            "连接失败": "网络连接问题或目标服务不可用",
            "connection failed": "连接建立失败",
            "内存不足": "系统内存资源耗尽",
            "out of memory": "内存溢出",
            "磁盘空间": "磁盘存储空间不足",
            "disk space": "磁盘空间问题",
            "CPU": "CPU资源使用率过高",
            "数据库": "数据库连接或查询问题",
            "database": "数据库相关问题",
            "权限": "访问权限不足或认证失败",
            "permission": "权限验证问题",
            "配置": "系统配置错误或缺失",
            "config": "配置相关问题",
            "aladdin": "aladdin服务相关问题",
            "SSL": "SSL证书或安全连接问题",
            "DNS": "域名解析问题",
            "负载": "系统负载过高",
            "load": "系统负载问题"
        }
        
        causes = []
        alert_lower = alert_details.lower()
        
        for keyword, description in keyword_mapping.items():
            if keyword.lower() in alert_lower:
                causes.append(f"关键词分析 - {keyword}: {description}")
                self.logger.debug(f"匹配关键词: {keyword}")
        
        return causes
    
    def _analyze_system_components(self, alert_details: str) -> List[str]:
        """分析涉及的系统组件"""
        components_found = []
        alert_lower = alert_details.lower()
        
        for component in SYSTEM_COMPONENTS:
            if component.lower() in alert_lower:
                components_found.append(component)
        
        causes = []
        if components_found:
            causes.append(f"涉及系统组件: {', '.join(components_found)}")
        
        return causes
    
    def _compare_with_history(self, alert_details: str) -> List[str]:
        """与历史数据比较分析"""
        historical_causes = []
        max_matches = self.config.get('max_historical_matches', 3)
        similarity_threshold = self.config.get('similarity_threshold', 0.6)
        
        similarities = []
        for event_id, event_data in self.knowledge_base.items():
            similarity = self._calculate_similarity(alert_details, event_data.get('description', ''))
            if similarity > similarity_threshold:
                similarities.append((similarity, event_id, event_data))
        
        # 按相似度排序，取前几个
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        for similarity, event_id, event_data in similarities[:max_matches]:
            historical_causes.append(
                f"历史事件相似性分析 ({similarity:.2f}): "
                f"事件 {event_id} - {event_data.get('cause', '未知原因')}"
            )
            self.logger.debug(f"匹配历史事件: {event_id}, 相似度: {similarity:.2f}")
        
        return historical_causes
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（改进版）"""
        # 简单的基于词汇重叠的相似度计算
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # Jaccard相似度
        jaccard = len(intersection) / len(union) if union else 0
        
        # 考虑长度差异的权重
        length_ratio = min(len(words1), len(words2)) / max(len(words1), len(words2))
        
        return jaccard * length_ratio
    
    def _assess_impact(self, alert_details: str) -> str:
        """评估影响范围和严重程度"""
        max_severity = "信息"
        max_weight = 0
        affected_systems = []
        
        # 基于关键词确定严重程度
        for severity, data in SEVERITY_KEYWORDS.items():
            for keyword in data["keywords"]:
                if keyword in alert_details:
                    if data["weight"] > max_weight:
                        max_weight = data["weight"]
                        max_severity = severity
        
        # 识别受影响的系统组件
        alert_lower = alert_details.lower()
        for component in SYSTEM_COMPONENTS:
            if component.lower() in alert_lower:
                affected_systems.append(component)
        
        # 构建影响评估描述
        impact_description = f"严重程度: {max_severity}"
        
        if affected_systems:
            impact_description += f"\n受影响的系统/服务: {', '.join(set(affected_systems))}"
        
        # 基于严重程度添加级联影响分析
        if max_severity in ["严重", "高"]:
            impact_description += "\n潜在级联影响: 高风险 - 可能导致业务中断，影响用户体验和业务收入"
        elif max_severity == "中":
            impact_description += "\n潜在级联影响: 中等风险 - 可能影响系统性能，需要密切监控"
        elif max_severity == "低":
            impact_description += "\n潜在级联影响: 低风险 - 轻微影响，可计划处理"
        
        # 添加影响范围估计
        if "用户" in alert_details or "业务" in alert_details:
            impact_description += "\n影响范围: 可能影响最终用户和业务流程"
        elif any(comp in alert_details for comp in ["数据库", "网络", "服务"]):
            impact_description += "\n影响范围: 主要影响系统内部组件"
        
        return impact_description
    
    def _generate_response_measures(self, alert_details: str, possible_causes: List[str]) -> str:
        """生成针对性的响应措施"""
        immediate_measures = []
        long_term_measures = []
        
        # 根据检测到的组件类型选择响应模板
        alert_lower = alert_details.lower()
        template_used = False
        
        # 检查是否是aladdin相关问题
        if "aladdin" in alert_lower:
            immediate_measures.extend(RESPONSE_TEMPLATES["aladdin"]["immediate"])
            long_term_measures.extend(RESPONSE_TEMPLATES["aladdin"]["long_term"])
            template_used = True
        
        # 检查是否是数据库相关问题
        if any(db_keyword in alert_lower for db_keyword in ["数据库", "database", "mysql", "postgresql", "redis"]):
            immediate_measures.extend(RESPONSE_TEMPLATES["database"]["immediate"])
            long_term_measures.extend(RESPONSE_TEMPLATES["database"]["long_term"])
            template_used = True
        
        # 检查是否是网络相关问题
        if any(net_keyword in alert_lower for net_keyword in ["网络", "network", "连接", "connection", "dns", "ssl"]):
            immediate_measures.extend(RESPONSE_TEMPLATES["network"]["immediate"])
            long_term_measures.extend(RESPONSE_TEMPLATES["network"]["long_term"])
            template_used = True
        
        # 检查是否是资源相关问题
        if any(res_keyword in alert_lower for res_keyword in ["cpu", "内存", "memory", "磁盘", "disk"]):
            immediate_measures.extend(RESPONSE_TEMPLATES["resource"]["immediate"])
            long_term_measures.extend(RESPONSE_TEMPLATES["resource"]["long_term"])
            template_used = True
        
        # 基于历史数据添加特定建议
        for cause in possible_causes:
            if "历史事件" in cause:
                # 从知识库中提取解决方案
                for event_id, event_data in self.knowledge_base.items():
                    if event_id in cause:
                        if 'solution' in event_data:
                            immediate_measures.append(f"参考历史解决方案: {event_data['solution']}")
                        if 'prevention' in event_data:
                            long_term_measures.append(f"预防措施: {event_data['prevention']}")
        
        # 如果没有使用模板，添加通用响应措施
        if not template_used:
            immediate_measures.extend([
                "立即检查相关系统日志以获取更多详细信息",
                "验证系统核心功能和服务可用性",
                "监控系统资源使用情况（CPU、内存、磁盘、网络）",
                "如有必要，联系相关技术团队或服务提供商"
            ])
            
            long_term_measures.extend([
                "建立更完善的监控和告警机制",
                "定期进行系统健康检查和性能评估",
                "完善故障应急响应流程和文档",
                "实施预防性维护计划"
            ])
        
        # 去重并格式化
        immediate_measures = list(dict.fromkeys(immediate_measures))  # 保持顺序的去重
        long_term_measures = list(dict.fromkeys(long_term_measures))
        
        response = "即时措施:\n"
        for i, measure in enumerate(immediate_measures, 1):
            response += f"{i}. {measure}\n"
        
        response += "\n长期措施:\n"
        for i, measure in enumerate(long_term_measures, 1):
            response += f"{i}. {measure}\n"
        
        return response.strip()
    
    def _format_analysis_result(self, possible_causes: List[str], 
                              impact_assessment: str, response_measures: str) -> str:
        """格式化分析结果"""
        result = "<analysis>\n"
        result += "<possible_causes>\n"
        for cause in possible_causes:
            result += f"• {cause}\n"
        result += "</possible_causes>\n\n"
        
        result += "<impact_assessment>\n"
        result += impact_assessment + "\n"
        result += "</impact_assessment>\n\n"
        
        result += "<response_measures>\n"
        result += response_measures + "\n"
        result += "</response_measures>\n"
        result += "</analysis>"
        
        return result
    
    def _format_error_response(self, error_message: str) -> str:
        """格式化错误响应"""
        return f"""<analysis>
<possible_causes>
• 分析过程中发生错误: {error_message}
</possible_causes>

<impact_assessment>
严重程度: 无法评估
影响范围: 分析系统异常
</impact_assessment>

<response_measures>
即时措施:
1. 检查告警分析系统状态和日志
2. 验证输入数据格式和完整性  
3. 手动分析告警信息作为备选方案
4. 联系技术支持团队

长期措施:
1. 修复分析系统的已知问题
2. 改进错误处理和容错机制
3. 增强系统监控和自动恢复能力
4. 定期进行系统健康检查
</response_measures>
</analysis>"""
    
    def add_historical_data(self, event_id: str, event_data: Dict[str, Any]):
        """添加历史数据到知识库"""
        self.knowledge_base[event_id] = event_data
        self.logger.info(f"添加历史事件: {event_id}")
    
    def update_error_code_mapping(self, error_code: str, meaning: str):
        """更新错误码映射"""
        self.error_code_mapping[error_code] = meaning
        self.logger.info(f"更新错误码映射: {error_code} -> {meaning}")
    
    def get_analysis_summary(self, alert_details: str) -> Dict[str, Any]:
        """获取分析摘要（结构化数据）"""
        try:
            possible_causes = self._identify_possible_causes(alert_details)
            impact_assessment = self._assess_impact(alert_details)
            
            # 提取严重程度
            severity_match = re.search(r'严重程度: (\w+)', impact_assessment)
            severity = severity_match.group(1) if severity_match else "未知"
            
            # 提取受影响系统
            systems_match = re.search(r'受影响的系统/服务: ([^\n]+)', impact_assessment)
            affected_systems = systems_match.group(1).split(', ') if systems_match else []
            
            return {
                "severity": severity,
                "affected_systems": affected_systems,
                "cause_count": len(possible_causes),
                "has_historical_match": any("历史事件" in cause for cause in possible_causes),
                "error_codes": self._extract_error_codes(alert_details),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"获取分析摘要失败: {str(e)}")
            return {"error": str(e)}


# 使用示例和测试用例
def main():
    """使用示例和测试"""
    # 初始化智能体
    agent = AlertAnalysisAgent()
    
    # 测试用例1: aladdin服务异常
    print("=" * 60)
    print("测试用例1: aladdin服务异常")
    print("=" * 60)
    
    test_alert_1 = """
    系统告警: aladdin服务异常
    时间: 2024-01-15 14:30:00
    错误码: 10015
    描述: aladdin请求超时，连接失败，用户无法登录
    影响: 用户无法正常访问相关功能，业务中断
    """
    
    result1 = agent.analyze_alert(test_alert_1)
    print(result1)
    
    # 测试用例2: 数据库连接问题
    print("\n" + "=" * 60)
    print("测试用例2: 数据库连接问题")
    print("=" * 60)
    
    test_alert_2 = """
    系统告警: 数据库连接失败
    时间: 2024-01-15 15:30:00
    错误码: 10006
    描述: MySQL数据库连接池耗尽，新连接无法建立
    影响: 系统无法读取用户数据，核心功能异常
    """
    
    result2 = agent.analyze_alert(test_alert_2)
    print(result2)
    
    # 测试用例3: 系统资源问题
    print("\n" + "=" * 60)
    print("测试用例3: 系统资源问题")
    print("=" * 60)
    
    test_alert_3 = """
    系统告警: 系统资源不足
    时间: 2024-01-15 16:30:00
    错误码: 10009
    描述: 内存使用率达到95%，CPU持续高负载，系统响应缓慢
    影响: 系统性能下降，用户体验受影响
    """
    
    result3 = agent.analyze_alert(test_alert_3)
    print(result3)
    
    # 获取分析摘要示例
    print("\n" + "=" * 60)
    print("分析摘要示例")
    print("=" * 60)
    
    summary = agent.get_analysis_summary(test_alert_1)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
