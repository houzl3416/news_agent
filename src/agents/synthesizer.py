"""
首席编辑 Agent (Synthesizer Agent)

职责：
1. 汇总所有Agent的发现
2. 生成格式化的溯源报告
3. 计算整体可信度评分
4. 准备EKG写入数据（更新知识图谱）
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, InvestigationContext, AgentResult, AgentStatus


class SynthesizerAgent(BaseAgent):
    """
    首席编辑 Agent
    负责汇总分析结果并生成最终报告
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="SynthesizerAgent", config=config)
        self.report_format = self.config.get("report_format", "detailed")

    async def execute(self, context: InvestigationContext) -> AgentResult:
        """
        执行报告生成

        Args:
            context: 调查上下文（包含所有Agent的发现）

        Returns:
            AgentResult: 包含最终报告
        """
        # 从context收集所有Agent的发现
        findings = context.findings

        # 生成报告
        report = await self._generate_report(context, findings)

        # 计算可信度评分
        credibility_score = await self._calculate_credibility_score(findings)

        # 准备EKG更新数据
        ekg_update = await self._prepare_ekg_update(context, findings, credibility_score)

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            data={
                "report": report,
                "credibility_score": credibility_score,
                "ekg_update": ekg_update,
                "investigation_id": context.investigation_id
            }
        )

    async def _generate_report(
        self,
        context: InvestigationContext,
        findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成调查报告

        Args:
            context: 调查上下文
            findings: 所有Agent的发现

        Returns:
            dict: 格式化报告
        """
        # TODO: 使用LLM生成自然语言报告

        original_source = findings.get("original_source", {})
        verification_results = findings.get("verification_results", [])
        narrative_analysis = findings.get("narrative_analysis", {})

        # 构建结构化报告
        report = {
            "investigation_id": context.investigation_id,
            "timestamp": datetime.now().isoformat(),
            "user_submission": context.user_submission,

            # 溯源结果
            "source_tracing": {
                "original_source": original_source.get("source_name", "Unknown"),
                "source_type": original_source.get("source_type", "Unknown"),
                "first_appearance": original_source.get("timestamp", "Unknown"),
                "confidence": original_source.get("confidence", 0.0)
            },

            # 核查结果
            "verification": {
                "claims_verified": len(verification_results),
                "overall_status": self._get_verification_status(verification_results),
                "details": verification_results
            },

            # 叙事分析
            "narrative_evolution": {
                "versions_analyzed": narrative_analysis.get("versions_count", 0),
                "evolution_detected": narrative_analysis.get("evolution", {}).get("changes", []),
                "suspicious_accounts": narrative_analysis.get("suspicious_accounts", [])
            },

            # 总结
            "summary": self._generate_summary(findings),

            # 建议
            "recommendation": self._generate_recommendation(findings)
        }

        return report

    def _get_verification_status(self, results: List[Dict[str, Any]]) -> str:
        """获取核查总体状态"""
        if not results:
            return "未核查"

        # 简化逻辑
        statuses = [r.get("status") for r in results]
        if "refuted" in statuses:
            return "存在证伪证据"
        elif all(s == "verified" for s in statuses):
            return "已验证"
        else:
            return "部分验证"

    def _generate_summary(self, findings: Dict[str, Any]) -> str:
        """
        生成摘要（核心发现）

        Args:
            findings: 所有发现

        Returns:
            str: 摘要文本
        """
        # TODO: 使用LLM生成更自然的摘要
        # 这里是框架示例

        original_source = findings.get("original_source", {})
        verification_results = findings.get("verification_results", [])

        summary_parts = []

        # 信源部分
        source_name = original_source.get("source_name", "未知来源")
        summary_parts.append(f"信息最早来自 {source_name}")

        # 核查部分
        refuted_count = sum(1 for r in verification_results if r.get("status") == "refuted")
        if refuted_count > 0:
            summary_parts.append(f"发现 {refuted_count} 项声明存在证伪证据")

        return "。".join(summary_parts) + "。"

    def _generate_recommendation(self, findings: Dict[str, Any]) -> str:
        """
        生成建议

        Args:
            findings: 所有发现

        Returns:
            str: 建议文本
        """
        verification_results = findings.get("verification_results", [])

        # 简化逻辑
        refuted_count = sum(1 for r in verification_results if r.get("status") == "refuted")

        if refuted_count > 0:
            return "建议：该信息存在多处不实之处，建议谨慎对待，等待官方确认。"
        else:
            return "建议：该信息尚未发现明显证伪证据，但建议持续关注官方渠道更新。"

    async def _calculate_credibility_score(self, findings: Dict[str, Any]) -> float:
        """
        计算可信度评分（0-100）

        Args:
            findings: 所有发现

        Returns:
            float: 可信度评分
        """
        # TODO: 更复杂的评分算法
        # 考虑因素：
        # 1. 信源历史信誉（从EKG查询）
        # 2. 核查结果
        # 3. 叙事演变模式
        # 4. 是否有水军参与

        score = 50.0  # 基准分

        # 根据核查结果调整
        verification_results = findings.get("verification_results", [])
        if verification_results:
            refuted_count = sum(1 for r in verification_results if r.get("status") == "refuted")
            verified_count = sum(1 for r in verification_results if r.get("status") == "verified")

            score -= refuted_count * 20  # 每个证伪 -20分
            score += verified_count * 10  # 每个验证 +10分

        # 根据叙事分析调整
        narrative_analysis = findings.get("narrative_analysis", {})
        if narrative_analysis.get("suspicious_accounts"):
            score -= 15  # 有水军参与 -15分

        # 限制在0-100范围
        return max(0.0, min(100.0, score))

    async def _prepare_ekg_update(
        self,
        context: InvestigationContext,
        findings: Dict[str, Any],
        credibility_score: float
    ) -> Dict[str, Any]:
        """
        准备EKG更新数据

        Args:
            context: 调查上下文
            findings: 所有发现
            credibility_score: 可信度评分

        Returns:
            dict: EKG更新数据（用于写入知识图谱）
        """
        original_source = findings.get("original_source", {})
        verification_results = findings.get("verification_results", [])

        # 构建EKG更新数据结构
        ekg_update = {
            # 事件节点
            "event": {
                "event_id": context.investigation_id,
                "status": "investigated",
                "credibility_score": credibility_score,
                "timestamp": datetime.now().isoformat()
            },

            # 信源节点
            "source": {
                "name": original_source.get("source_name", "Unknown"),
                "type": original_source.get("source_type", "unknown"),
                # 信誉分更新：根据本次调查结果
                "credit_score_change": self._calculate_source_credit_change(credibility_score)
            },

            # 声明节点
            "claims": [
                {
                    "text": r.get("claim"),
                    "status": r.get("status"),
                    "evidence": r.get("evidence", [])
                }
                for r in verification_results
            ],

            # 关系
            "relationships": {
                "event_has_claims": True,
                "source_made_claims": True,
                "claims_refuted_by": []  # 证伪关系
            }
        }

        return ekg_update

    def _calculate_source_credit_change(self, credibility_score: float) -> int:
        """
        计算信源信誉分变化（飞轮机制核心）

        Args:
            credibility_score: 本次调查的可信度评分

        Returns:
            int: 信誉分变化值（正数表示增加，负数表示减少）
        """
        # 规则：
        # - 可信度 >= 70: +5
        # - 可信度 30-70: 不变
        # - 可信度 < 30: -5

        if credibility_score >= 70:
            return 5
        elif credibility_score < 30:
            return -5
        else:
            return 0

    async def format_for_api(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化为API响应格式

        Args:
            report: 原始报告

        Returns:
            dict: API格式报告
        """
        # TODO: 根据TaaS API规范格式化
        return report

    async def format_for_ui(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化为UI展示格式

        Args:
            report: 原始报告

        Returns:
            dict: UI格式报告
        """
        # TODO: 添加UI需要的额外字段（如可视化数据）
        return report
