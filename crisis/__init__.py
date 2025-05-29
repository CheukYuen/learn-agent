"""
Crisis Agent - 智能告警分析系统

这个包提供了一个智能告警分析代理，能够分析系统告警并提供
全面的分析报告，包括潜在原因、影响评估和响应措施建议。
"""

from .analysis import AlertAnalysisAgent
from .config import (
    ERROR_CODE_MAPPING,
    KNOWLEDGE_BASE, 
    SEVERITY_KEYWORDS,
    SYSTEM_COMPONENTS,
    DEFAULT_CONFIG,
    RESPONSE_TEMPLATES
)

__version__ = "1.0.0"
__author__ = "Crisis Agent Team"
__description__ = "智能告警分析系统"

__all__ = [
    "AlertAnalysisAgent",
    "ERROR_CODE_MAPPING",
    "KNOWLEDGE_BASE",
    "SEVERITY_KEYWORDS", 
    "SYSTEM_COMPONENTS",
    "DEFAULT_CONFIG",
    "RESPONSE_TEMPLATES"
] 