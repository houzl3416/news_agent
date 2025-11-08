"""
Agent 模块

导出所有Agent类和相关数据结构
"""
from .base import (
    BaseAgent,
    InvestigationContext,
    AgentResult,
    AgentStatus
)

from .monitor import MonitorAgent
from .source_hunter import SourceHunterAgent
from .verifier import VerifierAgent, VerificationStatus
from .narrative import NarrativeAnalystAgent
from .synthesizer import SynthesizerAgent


__all__ = [
    # 基类和数据结构
    "BaseAgent",
    "InvestigationContext",
    "AgentResult",
    "AgentStatus",

    # 具体Agent
    "MonitorAgent",
    "SourceHunterAgent",
    "VerifierAgent",
    "NarrativeAnalystAgent",
    "SynthesizerAgent",

    # 枚举
    "VerificationStatus",
]
