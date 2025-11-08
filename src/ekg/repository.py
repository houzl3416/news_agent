"""
EKG 数据访问层 (Repository)

提供对知识图谱的CRUD操作
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import (
    Source, Event, Claim, Entity, Artifact,
    ClaimRefutation, InvestigationHistory,
    SourceType, EventStatus, ClaimStatus
)


class EKGRepository:
    """
    EKG 数据访问层
    封装所有数据库操作
    """

    def __init__(self, session: Session):
        """
        初始化Repository

        Args:
            session: SQLAlchemy Session
        """
        self.session = session

    # ============================================
    # Source (信源) 操作
    # ============================================

    def find_or_create_source(
        self,
        name: str,
        source_type: SourceType,
        **kwargs
    ) -> Source:
        """
        查找或创建信源

        Args:
            name: 信源名称
            source_type: 信源类型
            **kwargs: 其他属性

        Returns:
            Source: 信源对象
        """
        source = self.session.query(Source).filter_by(name=name).first()

        if not source:
            source = Source(
                name=name,
                type=source_type,
                **kwargs
            )
            self.session.add(source)
            self.session.commit()

        return source

    def get_source_by_name(self, name: str) -> Optional[Source]:
        """
        根据名称查询信源

        Args:
            name: 信源名称

        Returns:
            Source: 信源对象（如果存在）
        """
        return self.session.query(Source).filter_by(name=name).first()

    def update_source_credit_score(self, source_id: int, change: int) -> bool:
        """
        更新信源信誉分（飞轮机制核心）

        Args:
            source_id: 信源ID
            change: 信誉分变化值（正数或负数）

        Returns:
            bool: 是否更新成功
        """
        source = self.session.query(Source).filter_by(id=source_id).first()
        if not source:
            return False

        # 更新信誉分，限制在0-100范围
        new_score = max(0, min(100, source.credit_score + change))
        source.credit_score = new_score
        source.updated_at = datetime.utcnow()

        self.session.commit()
        return True

    def get_source_statistics(self, source_id: int) -> Dict[str, Any]:
        """
        获取信源统计数据

        Args:
            source_id: 信源ID

        Returns:
            dict: 统计数据
        """
        source = self.session.query(Source).filter_by(id=source_id).first()
        if not source:
            return {}

        return {
            "total_claims": source.total_claims,
            "verified_claims": source.verified_claims,
            "refuted_claims": source.refuted_claims,
            "accuracy_rate": (
                source.verified_claims / source.total_claims * 100
                if source.total_claims > 0 else 0
            ),
            "credit_score": source.credit_score
        }

    # ============================================
    # Event (事件) 操作
    # ============================================

    def create_event(self, event_id: str, **kwargs) -> Event:
        """
        创建事件

        Args:
            event_id: 事件ID
            **kwargs: 其他属性

        Returns:
            Event: 事件对象
        """
        event = Event(id=event_id, **kwargs)
        self.session.add(event)
        self.session.commit()
        return event

    def get_event(self, event_id: str) -> Optional[Event]:
        """
        获取事件

        Args:
            event_id: 事件ID

        Returns:
            Event: 事件对象
        """
        return self.session.query(Event).filter_by(id=event_id).first()

    def update_event_status(
        self,
        event_id: str,
        status: EventStatus,
        credibility_score: Optional[float] = None
    ) -> bool:
        """
        更新事件状态

        Args:
            event_id: 事件ID
            status: 新状态
            credibility_score: 可信度评分

        Returns:
            bool: 是否更新成功
        """
        event = self.get_event(event_id)
        if not event:
            return False

        event.status = status
        if credibility_score is not None:
            event.credibility_score = credibility_score
        event.updated_at = datetime.utcnow()

        self.session.commit()
        return True

    # ============================================
    # Claim (声明) 操作
    # ============================================

    def create_claim(
        self,
        text: str,
        source_id: int,
        event_id: Optional[str] = None,
        **kwargs
    ) -> Claim:
        """
        创建声明

        Args:
            text: 声明文本
            source_id: 信源ID
            event_id: 事件ID
            **kwargs: 其他属性

        Returns:
            Claim: 声明对象
        """
        claim = Claim(
            text=text,
            source_id=source_id,
            event_id=event_id,
            **kwargs
        )
        self.session.add(claim)

        # 更新信源统计
        source = self.session.query(Source).filter_by(id=source_id).first()
        if source:
            source.total_claims += 1

        self.session.commit()
        return claim

    def update_claim_status(
        self,
        claim_id: int,
        status: ClaimStatus,
        verification_result: Optional[Dict] = None
    ) -> bool:
        """
        更新声明状态

        Args:
            claim_id: 声明ID
            status: 新状态
            verification_result: 核查结果

        Returns:
            bool: 是否更新成功
        """
        claim = self.session.query(Claim).filter_by(id=claim_id).first()
        if not claim:
            return False

        old_status = claim.status
        claim.status = status

        if verification_result:
            claim.verification_result = verification_result

        # 更新信源统计
        source = claim.source
        if source:
            if old_status != ClaimStatus.VERIFIED and status == ClaimStatus.VERIFIED:
                source.verified_claims += 1
            elif old_status != ClaimStatus.REFUTED and status == ClaimStatus.REFUTED:
                source.refuted_claims += 1

        self.session.commit()
        return True

    def get_claims_by_event(self, event_id: str) -> List[Claim]:
        """
        获取事件的所有声明

        Args:
            event_id: 事件ID

        Returns:
            list: 声明列表
        """
        return self.session.query(Claim).filter_by(event_id=event_id).all()

    # ============================================
    # Entity (实体) 操作
    # ============================================

    def find_or_create_entity(
        self,
        name: str,
        entity_type: str,
        **kwargs
    ) -> Entity:
        """
        查找或创建实体

        Args:
            name: 实体名称
            entity_type: 实体类型
            **kwargs: 其他属性

        Returns:
            Entity: 实体对象
        """
        entity = self.session.query(Entity).filter_by(name=name).first()

        if not entity:
            entity = Entity(
                name=name,
                type=entity_type,
                **kwargs
            )
            self.session.add(entity)
            self.session.commit()

        return entity

    # ============================================
    # 关系操作
    # ============================================

    def create_claim_refutation(
        self,
        refuting_claim_id: int,
        refuted_claim_id: int,
        confidence: float = 1.0,
        evidence: Optional[List] = None
    ) -> ClaimRefutation:
        """
        创建声明证伪关系

        Args:
            refuting_claim_id: 证伪方声明ID
            refuted_claim_id: 被证伪声明ID
            confidence: 置信度
            evidence: 证据列表

        Returns:
            ClaimRefutation: 证伪关系对象
        """
        refutation = ClaimRefutation(
            refuting_claim_id=refuting_claim_id,
            refuted_claim_id=refuted_claim_id,
            confidence=confidence,
            evidence=evidence or []
        )
        self.session.add(refutation)
        self.session.commit()
        return refutation

    # ============================================
    # 调查历史操作
    # ============================================

    def save_investigation_result(
        self,
        investigation_id: str,
        event_id: str,
        report: Dict[str, Any],
        credibility_score: float,
        started_at: datetime
    ) -> InvestigationHistory:
        """
        保存调查结果

        Args:
            investigation_id: 调查ID
            event_id: 事件ID
            report: 调查报告
            credibility_score: 可信度评分
            started_at: 开始时间

        Returns:
            InvestigationHistory: 调查历史对象
        """
        history = InvestigationHistory(
            investigation_id=investigation_id,
            event_id=event_id,
            report=report,
            credibility_score=credibility_score,
            started_at=started_at
        )
        self.session.add(history)
        self.session.commit()
        return history

    def get_investigation_history(self, investigation_id: str) -> Optional[InvestigationHistory]:
        """
        获取调查历史

        Args:
            investigation_id: 调查ID

        Returns:
            InvestigationHistory: 调查历史对象
        """
        return self.session.query(InvestigationHistory).filter_by(
            investigation_id=investigation_id
        ).first()

    # ============================================
    # 复杂查询（飞轮效应相关）
    # ============================================

    def query_source_reputation(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        查询信源声誉（飞轮效应的"读"操作）

        Args:
            source_name: 信源名称

        Returns:
            dict: 信源声誉数据
        """
        source = self.get_source_by_name(source_name)
        if not source:
            return None

        return {
            "name": source.name,
            "type": source.type.value,
            "credit_score": source.credit_score,
            "statistics": self.get_source_statistics(source.id),
            "last_updated": source.updated_at.isoformat()
        }

    def find_similar_events(
        self,
        entities: List[str],
        limit: int = 5
    ) -> List[Event]:
        """
        查找相似事件（基于实体匹配）

        Args:
            entities: 实体列表
            limit: 返回数量

        Returns:
            list: 相似事件列表
        """
        # TODO: 实现更复杂的相似度算法
        # 简化版：查找包含相同实体的事件

        return []

    def get_trending_sources(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取热门信源（按活跃度）

        Args:
            limit: 返回数量

        Returns:
            list: 信源列表
        """
        sources = self.session.query(Source).order_by(
            Source.total_claims.desc()
        ).limit(limit).all()

        return [
            {
                "name": s.name,
                "type": s.type.value,
                "credit_score": s.credit_score,
                "total_claims": s.total_claims
            }
            for s in sources
        ]
