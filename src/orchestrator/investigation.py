"""
调查编排器 (Investigation Orchestrator)

职责：
1. 管理调查任务的生命周期
2. 按序调度各个Agent
3. 在Agent间传递上下文
4. 协调EKG的读写
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from ..agents import (
    BaseAgent,
    InvestigationContext,
    AgentResult,
    MonitorAgent,
    SourceHunterAgent,
    VerifierAgent,
    NarrativeAnalystAgent,
    SynthesizerAgent
)


class InvestigationOrchestrator:
    """
    调查编排器
    负责编排整个调查流程
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化编排器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.agents = self._initialize_agents()
        # TODO: 初始化EKG连接
        self.ekg = None

    def _initialize_agents(self) -> List[BaseAgent]:
        """
        初始化所有Agent

        Returns:
            list: Agent列表
        """
        # 按执行顺序排列
        agents = [
            MonitorAgent(self.config.get("monitor", {})),
            SourceHunterAgent(self.config.get("source_hunter", {})),
            VerifierAgent(self.config.get("verifier", {})),
            NarrativeAnalystAgent(self.config.get("narrative", {})),
            SynthesizerAgent(self.config.get("synthesizer", {}))
        ]

        return agents

    async def start_investigation(
        self,
        submission: str,
        submission_type: str = "url"
    ) -> Dict[str, Any]:
        """
        启动调查流程（核心方法）

        Args:
            submission: 用户提交的链接或文本
            submission_type: 提交类型（"url" 或 "text"）

        Returns:
            dict: 调查结果（包含报告）
        """
        # 1. 创建调查上下文
        investigation_id = self._generate_investigation_id()
        context = InvestigationContext(
            investigation_id=investigation_id,
            user_submission=submission,
            submission_type=submission_type,
            timestamp=datetime.now()
        )

        # 2. 查询EKG历史数据（快速预警）
        historical_data = await self._query_ekg_history(submission)
        if historical_data:
            context.metadata["historical_data"] = historical_data

        # 3. 按顺序执行Agent Pipeline
        agent_results = []
        for agent in self.agents:
            result = await agent.run(context)
            agent_results.append(result)

            # 如果关键Agent失败，可选择中止流程
            if not result.is_success() and self._is_critical_agent(agent):
                break

        # 4. 从最后的Synthesizer结果中提取报告和EKG更新数据
        final_result = agent_results[-1] if agent_results else None
        if final_result and final_result.is_success():
            report = final_result.data.get("report", {})
            ekg_update = final_result.data.get("ekg_update", {})

            # 5. 更新EKG（飞轮机制）
            await self._update_ekg(ekg_update)

            return {
                "investigation_id": investigation_id,
                "status": "completed",
                "report": report,
                "credibility_score": final_result.data.get("credibility_score", 0.0),
                "agent_results": [
                    {
                        "agent": r.agent_name,
                        "status": r.status.value,
                        "execution_time": r.execution_time
                    }
                    for r in agent_results
                ]
            }
        else:
            return {
                "investigation_id": investigation_id,
                "status": "failed",
                "error": "Investigation pipeline failed",
                "agent_results": agent_results
            }

    async def _query_ekg_history(self, submission: str) -> Optional[Dict[str, Any]]:
        """
        查询EKG历史数据（飞轮效应的"读"操作）

        Args:
            submission: 用户提交内容

        Returns:
            dict: 历史数据（如果有）
        """
        # TODO: 实现EKG查询
        # 1. 提取关键实体
        # 2. 在EKG中查找相关信源的历史信誉
        # 3. 查找类似事件的历史记录

        if not self.ekg:
            return None

        # 框架示例
        return {
            "similar_events": [],
            "source_reputation": None
        }

    async def _update_ekg(self, ekg_update: Dict[str, Any]) -> bool:
        """
        更新EKG（飞轮效应的"写"操作）

        Args:
            ekg_update: EKG更新数据

        Returns:
            bool: 是否更新成功
        """
        # TODO: 实现EKG写入
        # 1. 写入事件节点
        # 2. 写入/更新信源节点
        # 3. 写入声明节点
        # 4. 更新关系
        # 5. 更新信源信誉分（飞轮核心）

        if not self.ekg:
            return False

        # 框架示例
        return True

    def _is_critical_agent(self, agent: BaseAgent) -> bool:
        """
        判断Agent是否为关键Agent（失败会中止流程）

        Args:
            agent: Agent实例

        Returns:
            bool: 是否关键
        """
        # SourceHunter和Synthesizer是关键Agent
        critical_agents = ["SourceHunterAgent", "SynthesizerAgent"]
        return agent.__class__.__name__ in critical_agents

    def _generate_investigation_id(self) -> str:
        """
        生成调查ID

        Returns:
            str: 调查ID（如 E-1024）
        """
        # 使用UUID确保唯一性
        return f"E-{uuid.uuid4().hex[:8]}"

    async def get_investigation_status(self, investigation_id: str) -> Dict[str, Any]:
        """
        查询调查状态

        Args:
            investigation_id: 调查ID

        Returns:
            dict: 调查状态
        """
        # TODO: 从数据库或缓存查询调查状态
        return {
            "investigation_id": investigation_id,
            "status": "unknown"
        }

    async def cancel_investigation(self, investigation_id: str) -> bool:
        """
        取消调查

        Args:
            investigation_id: 调查ID

        Returns:
            bool: 是否取消成功
        """
        # TODO: 实现调查取消逻辑
        return False
