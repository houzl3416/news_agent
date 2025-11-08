"""
监控哨兵 Agent (Monitor Agent)

职责：
1. 接收用户提交的新闻链接或事件描述（核心触发方式）
2. 周期性巡查特选信源列表，检测热度异常（演示功能）
3. 触发调查任务
"""
from typing import Dict, Any, List
from .base import BaseAgent, InvestigationContext, AgentResult, AgentStatus


class MonitorAgent(BaseAgent):
    """
    监控哨兵 Agent
    负责检测和触发调查任务
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="MonitorAgent", config=config)
        self.monitored_sources = self.config.get("monitored_sources", [])
        self.keyword_threshold = self.config.get("keyword_threshold", 100)

    async def execute(self, context: InvestigationContext) -> AgentResult:
        """
        执行监控逻辑

        对于用户提交：直接标记为需要调查
        对于周期性监控：分析热度和关键词

        Args:
            context: 调查上下文

        Returns:
            AgentResult: 监控结果
        """
        # TODO: 实现监控逻辑
        # 1. 如果是用户提交，直接返回"需要调查"
        # 2. 如果是周期性监控，分析关键词热度

        trigger_reason = "user_submission"  # 或 "keyword_surge"

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            data={
                "should_investigate": True,
                "trigger_reason": trigger_reason,
                "confidence": 0.9,
                "metadata": {
                    "submission_type": context.submission_type,
                    "timestamp": context.timestamp.isoformat()
                }
            }
        )

    async def detect_keyword_surge(self, keywords: List[str]) -> Dict[str, Any]:
        """
        检测关键词热度激增（周期性监控功能）

        Args:
            keywords: 关键词列表

        Returns:
            dict: 热度分析结果
        """
        # TODO: 实现关键词热度检测
        # 1. 查询搜索引擎API
        # 2. 对比历史基线
        # 3. 判断是否激增

        return {
            "surge_detected": False,
            "heat_score": 0.0,
            "keywords": keywords
        }

    async def check_monitored_sources(self) -> List[Dict[str, Any]]:
        """
        检查特选信源列表（周期性任务）

        Returns:
            list: 检测到的可疑事件列表
        """
        # TODO: 实现信源巡查
        # 1. 遍历monitored_sources
        # 2. 抓取最新内容
        # 3. 识别异常模式

        return []
