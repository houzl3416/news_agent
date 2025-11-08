"""
EKG 图操作 (Graph Operations)

提供高级图查询和分析功能
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict, deque

from .repository import EKGRepository
from .models import Source, Event, Claim


class EKGGraphOps:
    """
    EKG 图操作类
    提供图遍历、路径查找、关系分析等功能
    """

    def __init__(self, repository: EKGRepository):
        """
        初始化图操作

        Args:
            repository: EKG数据访问层
        """
        self.repo = repository

    # ============================================
    # 图遍历和路径查找
    # ============================================

    def find_claim_propagation_path(
        self,
        origin_claim_id: int,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        查找声明的传播路径

        Args:
            origin_claim_id: 原始声明ID
            max_depth: 最大深度

        Returns:
            list: 传播路径（图的层次结构）
        """
        # TODO: 实现BFS遍历传播路径
        # 这需要先建立声明之间的引用/转发关系表

        return []

    def find_refutation_chain(
        self,
        claim_id: int
    ) -> List[Dict[str, Any]]:
        """
        查找声明的证伪链

        Args:
            claim_id: 声明ID

        Returns:
            list: 证伪链（哪些声明证伪了它，或它证伪了哪些）
        """
        # TODO: 通过ClaimRefutation表构建证伪链

        return []

    # ============================================
    # 关系分析
    # ============================================

    def analyze_source_network(
        self,
        source_ids: List[int]
    ) -> Dict[str, Any]:
        """
        分析信源网络（检测协同行为）

        Args:
            source_ids: 信源ID列表

        Returns:
            dict: 网络分析结果
        """
        # TODO: 分析信源之间的协同模式
        # 1. 检查是否发布相似内容
        # 2. 检查发布时间的相关性
        # 3. 计算网络密度

        return {
            "coordinated": False,
            "confidence": 0.0,
            "patterns": []
        }

    def detect_bot_cluster(
        self,
        source_ids: List[int],
        similarity_threshold: float = 0.8
    ) -> List[Set[int]]:
        """
        检测水军集群

        Args:
            source_ids: 信源ID列表
            similarity_threshold: 相似度阈值

        Returns:
            list: 集群列表（每个集群是一个信源ID集合）
        """
        # TODO: 使用聚类算法检测水军
        # 特征：
        # 1. 注册时间接近
        # 2. 发布内容高度相似
        # 3. 活跃时间同步

        return []

    # ============================================
    # 统计和聚合
    # ============================================

    def calculate_event_credibility(
        self,
        event_id: str
    ) -> Dict[str, Any]:
        """
        计算事件整体可信度

        Args:
            event_id: 事件ID

        Returns:
            dict: 可信度分析
        """
        event = self.repo.get_event(event_id)
        if not event:
            return {"error": "Event not found"}

        claims = self.repo.get_claims_by_event(event_id)

        if not claims:
            return {
                "credibility_score": 50.0,
                "confidence": "low",
                "reason": "No claims to verify"
            }

        # 统计声明状态
        verified_count = sum(1 for c in claims if c.status.value == "verified")
        refuted_count = sum(1 for c in claims if c.status.value == "refuted")
        total = len(claims)

        # 计算可信度
        score = 50.0  # 基准
        score += (verified_count / total) * 30  # 已验证提升分数
        score -= (refuted_count / total) * 40   # 已证伪降低分数

        # 考虑信源信誉
        source_scores = []
        for claim in claims:
            if claim.source:
                source_scores.append(claim.source.credit_score)

        if source_scores:
            avg_source_score = sum(source_scores) / len(source_scores)
            score = score * 0.7 + avg_source_score * 0.3  # 加权

        return {
            "credibility_score": round(score, 2),
            "verified_claims": verified_count,
            "refuted_claims": refuted_count,
            "total_claims": total,
            "confidence": "high" if total >= 3 else "low"
        }

    def get_source_influence_score(
        self,
        source_id: int
    ) -> float:
        """
        计算信源影响力分数

        Args:
            source_id: 信源ID

        Returns:
            float: 影响力分数
        """
        # TODO: 基于PageRank或类似算法计算影响力
        # 考虑因素：
        # 1. 被引用次数
        # 2. 引用者的影响力
        # 3. 内容准确率

        return 0.0

    # ============================================
    # 可视化数据生成
    # ============================================

    def generate_event_graph(
        self,
        event_id: str
    ) -> Dict[str, Any]:
        """
        生成事件图谱（用于可视化）

        Args:
            event_id: 事件ID

        Returns:
            dict: 图谱数据（节点和边）
        """
        event = self.repo.get_event(event_id)
        if not event:
            return {"nodes": [], "edges": []}

        claims = self.repo.get_claims_by_event(event_id)

        nodes = []
        edges = []

        # 事件节点
        nodes.append({
            "id": event.id,
            "type": "event",
            "label": event.title or event.id,
            "credibility": event.credibility_score
        })

        # 声明节点
        for claim in claims:
            nodes.append({
                "id": f"claim-{claim.id}",
                "type": "claim",
                "label": claim.text[:50] + "...",
                "status": claim.status.value
            })

            # 事件-声明边
            edges.append({
                "from": event.id,
                "to": f"claim-{claim.id}",
                "type": "has_claim"
            })

            # 信源节点
            if claim.source:
                source_node_id = f"source-{claim.source.id}"

                # 检查是否已添加
                if not any(n["id"] == source_node_id for n in nodes):
                    nodes.append({
                        "id": source_node_id,
                        "type": "source",
                        "label": claim.source.name,
                        "credit_score": claim.source.credit_score
                    })

                # 信源-声明边
                edges.append({
                    "from": source_node_id,
                    "to": f"claim-{claim.id}",
                    "type": "made_claim"
                })

        return {
            "nodes": nodes,
            "edges": edges
        }

    def generate_propagation_timeline(
        self,
        event_id: str
    ) -> List[Dict[str, Any]]:
        """
        生成传播时间线

        Args:
            event_id: 事件ID

        Returns:
            list: 时间线数据
        """
        claims = self.repo.get_claims_by_event(event_id)

        # 按时间排序
        timeline = sorted(
            [
                {
                    "timestamp": claim.timestamp.isoformat(),
                    "source": claim.source.name if claim.source else "Unknown",
                    "claim": claim.text[:100],
                    "status": claim.status.value
                }
                for claim in claims
            ],
            key=lambda x: x["timestamp"]
        )

        return timeline

    # ============================================
    # 批量操作
    # ============================================

    def batch_update_source_scores(
        self,
        investigation_results: List[Dict[str, Any]]
    ) -> int:
        """
        批量更新信源信誉分

        Args:
            investigation_results: 调查结果列表

        Returns:
            int: 更新数量
        """
        updated = 0

        for result in investigation_results:
            source_id = result.get("source_id")
            score_change = result.get("score_change")

            if source_id and score_change is not None:
                if self.repo.update_source_credit_score(source_id, score_change):
                    updated += 1

        return updated
